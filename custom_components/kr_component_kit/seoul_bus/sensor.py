"""Seoul Bus arrival sensors — TIMESTAMP based."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from ..const import DOMAIN

KST = timezone(timedelta(hours=9))


def _parse_int(val: Any) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


class SeoulBusArrivalSensor(CoordinatorEntity, SensorEntity):
    """One sensor per (station, route, slot).  slot 0 = next, slot 1 = the one after."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:bus-clock"

    def __init__(self, coordinator, route: str, index: int, device_info) -> None:
        super().__init__(coordinator)
        self._route = route
        self._idx = index
        suffix = "now" if index == 0 else "next"
        self._attr_unique_id = (
            f"{DOMAIN}_seoul_bus_{coordinator.ars_id}_{route}_{suffix}"
        )
        # Explicit ASCII entity_id keeps automations portable and avoids
        # Hangul transcription artefacts in the slug.  Matches the
        # convention shipped by Murianwind/seoul_bus.
        self.entity_id = (
            f"sensor.seoul_bus_{slugify(coordinator.ars_id)}_"
            f"{slugify(route)}_{suffix}"
        )
        self._attr_name = f"{route} 다음" if index == 0 else f"{route} 다다음"
        self._attr_device_info = device_info

    def _item(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        return data.get(self._route)

    @property
    def native_value(self) -> datetime | None:
        item = self._item()
        if not item:
            return None
        key = "traTime1" if self._idx == 0 else "traTime2"
        seconds = _parse_int(item.get(key))
        if seconds <= 0:
            return None
        return datetime.now(KST) + timedelta(seconds=seconds)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        item = self._item()
        if not item:
            return {}
        idx = self._idx
        msg_key = f"arrmsg{idx + 1}"
        plain_key = f"plainNo{idx + 1}"
        time_key = f"traTime{idx + 1}"
        # Slot-aware keys for the new attrs (v4.7.0).  The official 활용
        # guide names them with a trailing 1/2 — same convention as the
        # other slot fields above.
        full_key = f"isFullFlag{idx + 1}"
        congestion_key = f"congestion{idx + 1}"
        reride_key = f"rerideNum{idx + 1}"
        remndr_key = f"remndrNmpr{idx + 1}"
        bustype_key = f"busType{idx + 1}"
        seconds = _parse_int(item.get(time_key))

        # Map per the activity guide:
        # busType  — 0:일반, 1:저상, 2:굴절
        # congestion — 3:여유, 4:보통, 5:혼잡
        bus_type_label = {"0": "일반", "1": "저상", "2": "굴절"}.get(
            str(item.get(bustype_key) or ""), "")
        congestion_label = {"3": "여유", "4": "보통", "5": "혼잡"}.get(
            str(item.get(congestion_key) or ""), "")

        attrs: dict[str, Any] = {
            "message": item.get(msg_key) or "정보 없음",
            "vehicle_no": item.get(plain_key) or "",
            "route_id": item.get("busRouteId") or "",
            "direction": item.get("nxtStn") or "",
            # New in v4.7.0 — these come straight from getStationByUidItem
            # and surface what users of 활용사례 buses-apps expect:
            # congestion / full / seating / vehicle type for accessibility.
            "is_full": str(item.get(full_key) or "") == "1",
            "is_low_floor": str(item.get(bustype_key) or "") == "1",
            "bus_type_code": item.get(bustype_key) or "",
            "bus_type": bus_type_label,
            "congestion_code": item.get(congestion_key) or "",
            "congestion": congestion_label,
            "passengers_aboard": _parse_int(item.get(reride_key)),
            "remaining_seats": _parse_int(item.get(remndr_key)),
        }
        if seconds > 0:
            attrs["remaining_seconds"] = seconds
            attrs["status"] = "곧 도착" if seconds <= 60 else f"{seconds // 60}분 후"
        elif item.get(msg_key):
            # API returned a message but no seconds — usually "운행종료" / "출발대기".
            attrs["status"] = item[msg_key]
        return attrs
