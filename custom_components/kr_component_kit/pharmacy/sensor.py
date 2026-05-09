"""Pharmacy sensor - count + per-pharmacy detail attributes."""
from __future__ import annotations
from datetime import datetime
from typing import Any
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from ..const import DOMAIN, TZ_ASIA_SEOUL, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION

# HA caps state-attribute size around 16KB; ~50 pharmacies × ~200B fits
# comfortably while still covering most 시군구 selections.
_MAX_ATTR_PHARMACIES = 50

_DAY_NAMES_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _today_hours(duty_time: dict[str, str]) -> str | None:
    today = _DAY_NAMES_KO[datetime.now(TZ_ASIA_SEOUL).weekday()]
    return duty_time.get(today) or duty_time.get("공휴일")


def _is_open_now(duty_time: dict[str, str], now: datetime) -> bool:
    """Return True if current KST time falls inside today's duty window.

    Duty hours format from data.go.kr is "HHMM~HHMM" (e.g. "0900~2200").
    Closing < opening means an overnight shift (e.g. "2200~0600").
    """
    spec = duty_time.get(_DAY_NAMES_KO[now.weekday()]) or duty_time.get("공휴일")
    if not spec or "~" not in spec:
        return False
    try:
        start_str, close_str = (s.strip() for s in spec.split("~", 1))
        if len(start_str) != 4 or len(close_str) != 4:
            return False
        start_min = int(start_str[:2]) * 60 + int(start_str[2:])
        close_min = int(close_str[:2]) * 60 + int(close_str[2:])
    except ValueError:
        return False
    cur = now.hour * 60 + now.minute
    if close_min <= start_min:
        # overnight window — current time is within the window if it's
        # past the start OR before the close on the wrap-around side
        return cur >= start_min or cur <= close_min
    return start_min <= cur <= close_min


class PharmacySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:pharmacy"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, q0: str, q1: str) -> None:
        super().__init__(coordinator)
        label = q1 if q1 else q0
        self._attr_unique_id = f"{DOMAIN}_pharmacy_{q0}_{q1}"
        self._attr_name = "운영 약국 수"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"pharmacy_{q0}_{q1}")},
            name=f"약국 - {label}",
            manufacturer=DONATION_MANUFACTURER,
            model=DONATION_MODEL,
            sw_version=DONATION_SW_VERSION,
            entry_type=DeviceEntryType.SERVICE)

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or []
        # Sort by name for stable rendering, then truncate.
        sorted_data = sorted(data, key=lambda p: p.get("name") or "")
        # Property is read on each state access, so `now` reflects the
        # request time — open_now stays roughly fresh between coordinator
        # refreshes (sufficient for hour-level pharmacy schedules).
        now = datetime.now(TZ_ASIA_SEOUL)
        pharmacies: list[dict[str, Any]] = []
        for ph in sorted_data[:_MAX_ATTR_PHARMACIES]:
            duty = ph.get("duty_time") or {}
            pharmacies.append({
                "name": ph.get("name") or "",
                "address": ph.get("address") or "",
                "phone": ph.get("phone") or "",
                "today_hours": _today_hours(duty) or "",
                "open_now": _is_open_now(duty, now),
                "duty_time": duty,
                "lat": ph.get("lat") or "",
                "lon": ph.get("lon") or "",
            })
        return {
            "pharmacies": pharmacies,
            "total": len(data),
            "shown": len(pharmacies),
            "open_now_count": sum(1 for p in pharmacies if p["open_now"]),
        }
