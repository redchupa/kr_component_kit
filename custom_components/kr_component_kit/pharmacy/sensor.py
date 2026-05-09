"""Pharmacy sensor - count + per-pharmacy detail attributes."""
from __future__ import annotations
from datetime import datetime
from typing import Any
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from ..const import DOMAIN, TZ_ASIA_SEOUL

# HA caps state-attribute size around 16KB; ~50 pharmacies × ~200B fits
# comfortably while still covering most 시군구 selections.
_MAX_ATTR_PHARMACIES = 50

_DAY_NAMES_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _today_hours(duty_time: dict[str, str]) -> str | None:
    today = _DAY_NAMES_KO[datetime.now(TZ_ASIA_SEOUL).weekday()]
    return duty_time.get(today) or duty_time.get("공휴일")


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
            name=f"약국 - {label}", manufacturer="건강보험심사평가원",
            model="약국 운영정보", entry_type=DeviceEntryType.SERVICE)

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or []
        # Sort by name for stable rendering, then truncate.
        sorted_data = sorted(data, key=lambda p: p.get("name") or "")
        pharmacies: list[dict[str, Any]] = []
        for ph in sorted_data[:_MAX_ATTR_PHARMACIES]:
            duty = ph.get("duty_time") or {}
            pharmacies.append({
                "name": ph.get("name") or "",
                "address": ph.get("address") or "",
                "phone": ph.get("phone") or "",
                "today_hours": _today_hours(duty) or "",
                "duty_time": duty,
                "lat": ph.get("lat") or "",
                "lon": ph.get("lon") or "",
            })
        return {
            "pharmacies": pharmacies,
            "total": len(data),
            "shown": len(pharmacies),
        }
