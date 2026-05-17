"""Korea Bus arrival sensors — TIMESTAMP based."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from ..const import DOMAIN

KST = timezone(timedelta(hours=9))

# KakaoMap busesInBusStopJson exposes the next two arrivals under suffixed
# keys; index 0 reads the unsuffixed key, index 1 reads the "2" key.
_KEYS = [
    {  # slot 0 — next arrival
        "time": "arrivalTime",
        "vehicle": "vehicleNumber",
        "current": "currentBusStopName",
        "message": "vehicleStateMessage",
        "remain_seat": "remainSeat",
        "updated_at": "collectDateTime",
        "last_vehicle": "lastVehicle",
        "stop_count": "busStopCount",
    },
    {  # slot 1 — the one after
        "time": "arrivalTime2",
        "vehicle": "vehicleNumber2",
        "current": "currentBusStopName2",
        "message": "vehicleStateMessage2",
        "remain_seat": "remainSeat2",
        "updated_at": "collectDateTime2",
        "last_vehicle": "lastVehicle2",
        "stop_count": "busStopCount2",
    },
]


def _parse_int(val: Any) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _format_collect_dt(raw: Any) -> str:
    if not raw:
        return ""
    try:
        return datetime.strptime(str(raw), "%Y%m%d%H%M%S").strftime(
            "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return str(raw)


class KoreaBusArrivalSensor(CoordinatorEntity, SensorEntity):
    """One sensor per (stop, route, slot).  slot 0 = next, slot 1 = the one after."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:bus-clock"

    def __init__(self, coordinator, route: str, index: int, device_info) -> None:
        super().__init__(coordinator)
        self._route = route
        self._idx = index
        self._k = _KEYS[index]
        suffix = "now" if index == 0 else "next"
        self._attr_unique_id = (
            f"{DOMAIN}_korea_bus_{coordinator.stop_id}_{route}_{suffix}"
        )
        # ASCII entity_id so automations / dashboards don't have to deal
        # with Hangul transcription artefacts.
        self.entity_id = (
            f"sensor.korea_bus_{slugify(coordinator.stop_id)}_"
            f"{slugify(route)}_{suffix}"
        )
        self._attr_name = f"{route} 다음" if index == 0 else f"{route} 다다음"
        self._attr_device_info = device_info

    def _bus(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        return data.get(self._route)

    @property
    def native_value(self) -> datetime | None:
        bus = self._bus()
        if not bus:
            return None
        seconds = _parse_int(bus.get(self._k["time"]))
        if seconds <= 0:
            return None
        return datetime.now(KST) + timedelta(seconds=seconds)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        bus = self._bus()
        if not bus:
            return {}
        seconds = _parse_int(bus.get(self._k["time"]))
        attrs: dict[str, Any] = {
            "vehicle_number": bus.get(self._k["vehicle"]) or "",
            "current_stop": bus.get(self._k["current"]) or "",
            "message": bus.get(self._k["message"]) or "",
            "remain_seat": bus.get(self._k["remain_seat"]) or "",
            "stop_count": bus.get(self._k["stop_count"]) or "",
            "last_vehicle": bus.get(self._k["last_vehicle"]) or "",
            "updated_at": _format_collect_dt(bus.get(self._k["updated_at"])),
        }
        # Slot 0 also carries route-level metadata (direction, type, schedule).
        if self._idx == 0:
            attrs.update({
                "direction": bus.get("direction") or "",
                "bus_type": bus.get("typeName") or "",
                "first_time": bus.get("first") or "",
                "last_time": bus.get("last") or "",
                "intervals": bus.get("intervals") or "",
                "next_stop": bus.get("nextBusStopName") or "",
            })
        if seconds > 0:
            attrs["remaining_seconds"] = seconds
            attrs["status"] = "곧 도착" if seconds <= 60 else f"{seconds // 60}분 후"
        elif bus.get(self._k["message"]):
            attrs["status"] = bus[self._k["message"]]
        return attrs
