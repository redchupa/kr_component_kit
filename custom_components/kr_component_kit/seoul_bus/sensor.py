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
        msg_key = "arrmsg1" if self._idx == 0 else "arrmsg2"
        plain_key = "plainNo1" if self._idx == 0 else "plainNo2"
        time_key = "traTime1" if self._idx == 0 else "traTime2"
        seconds = _parse_int(item.get(time_key))
        attrs: dict[str, Any] = {
            "message": item.get(msg_key) or "정보 없음",
            "vehicle_no": item.get(plain_key) or "",
            "route_id": item.get("busRouteId") or "",
            "direction": item.get("nxtStn") or "",
        }
        if seconds > 0:
            attrs["remaining_seconds"] = seconds
            attrs["status"] = "곧 도착" if seconds <= 60 else f"{seconds // 60}분 후"
        elif item.get(msg_key):
            # API returned a message but no seconds — usually "운행종료" / "출발대기".
            attrs["status"] = item[msg_key]
        return attrs
