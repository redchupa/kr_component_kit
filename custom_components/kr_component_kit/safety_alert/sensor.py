"""Safety Alert sensors, binary sensor and event entity."""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.event import EventEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..utils import TZ_ASIA_SEOUL, parse_date_value
from .coordinator import SafetyAlertCoordinator


def _safety_alert_device(area_code: str, area_name: str) -> DeviceInfo:
    label = f"안전알림 ({area_name})" if area_name else "안전알림"
    return DeviceInfo(
        identifiers={(DOMAIN, f"safety_alert_{area_code}")},
        name=label,
        manufacturer="행정안전부",
        model="안전알림서비스",
        configuration_url="https://www.safekorea.go.kr",
        entry_type=DeviceEntryType.SERVICE,
    )


def _alerts(coordinator: SafetyAlertCoordinator) -> list[dict[str, Any]]:
    if not coordinator.data:
        return []
    return coordinator.data.get("parsed_data", {}).get("data", []) or []


def _format_alert(a: dict[str, Any]) -> dict[str, Any]:
    return {
        "emergency_step": a.get("EMRGNCY_STEP_NM"),
        "disaster_type": a.get("DSSTR_SE_NM"),
        "message": a.get("MSG_CN"),
        "reception_area": a.get("RCV_AREA_NM"),
        "registration_date": a.get("REGIST_DT"),
    }


class SafetyAlertTextSensor(CoordinatorEntity[SafetyAlertCoordinator], SensorEntity):
    """Latest safety alert message as state, full list as attribute."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:message-alert"

    def __init__(
        self,
        coordinator: SafetyAlertCoordinator,
        area_code: str,
        area_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._area_code = area_code
        self._attr_name = "최신 안전알림"
        self._attr_unique_id = f"{DOMAIN}_safety_alert_latest_{area_code}"
        self._attr_device_info = _safety_alert_device(area_code, area_name)

    @property
    def native_value(self) -> str | None:
        alerts = _alerts(self.coordinator)
        if not alerts:
            return "없음"
        msg = alerts[0].get("MSG_CN") or ""
        return msg[:255] if msg else "없음"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        alerts = _alerts(self.coordinator)
        formatted = [_format_alert(a) for a in alerts]
        return {
            "latest": formatted[0] if formatted else None,
            "alerts": formatted,
            "count": len(formatted),
        }


class SafetyAlertCountSensor(CoordinatorEntity[SafetyAlertCoordinator], SensorEntity):
    """Total count of safety alerts."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "건"

    def __init__(
        self,
        coordinator: SafetyAlertCoordinator,
        area_code: str,
        area_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = "안전알림 수"
        self._attr_unique_id = f"{DOMAIN}_safety_alert_count_{area_code}"
        self._attr_device_info = _safety_alert_device(area_code, area_name)

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("metadata", {}).get("count", 0)


class SafetyAlertBinarySensor(
    CoordinatorEntity[SafetyAlertCoordinator], BinarySensorEntity
):
    """ON when the most recent alert was issued today."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(
        self,
        coordinator: SafetyAlertCoordinator,
        area_code: str,
        area_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = "안전알림"
        self._attr_unique_id = f"{DOMAIN}_safety_alert_active_{area_code}"
        self._attr_device_info = _safety_alert_device(area_code, area_name)

    @property
    def is_on(self) -> bool | None:
        alerts = _alerts(self.coordinator)
        if not alerts:
            return False
        latest = alerts[0]
        if not latest.get("EMRGNCY_STEP_NM"):
            return False
        regist_dt = parse_date_value(latest.get("REGIST_DT"))
        if regist_dt is None:
            return False
        today_start = datetime.combine(
            date.today(), time(0, 0, 0), tzinfo=TZ_ASIA_SEOUL
        )
        return regist_dt >= today_start

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        alerts = _alerts(self.coordinator)
        formatted = [_format_alert(a) for a in alerts]
        return {
            "latest": formatted[0] if formatted else None,
            "alerts": formatted,
        }


class SafetyAlertEvent(CoordinatorEntity[SafetyAlertCoordinator], EventEntity):
    """Fires whenever a new alert appears at the top of the list."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:alert-circle"
    _attr_event_types = ["emergency", "urgent", "safety", "alert"]

    def __init__(
        self,
        coordinator: SafetyAlertCoordinator,
        area_code: str,
        area_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = "안전알림 이벤트"
        self._attr_unique_id = f"{DOMAIN}_safety_alert_event_{area_code}"
        self._attr_device_info = _safety_alert_device(area_code, area_name)
        self._last_id: str | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        alerts = _alerts(self.coordinator)
        if not alerts:
            return
        latest = alerts[0]
        msg_id = latest.get("REGIST_DT") or latest.get("MSG_CN", "")[:32]
        if self._last_id is not None and msg_id and msg_id != self._last_id:
            step = (latest.get("EMRGNCY_STEP_NM") or "").strip()
            event_type = "alert"
            if "위급" in step:
                event_type = "emergency"
            elif "긴급" in step:
                event_type = "urgent"
            elif "안전" in (latest.get("DSSTR_SE_NM") or ""):
                event_type = "safety"
            self._trigger_event(event_type, _format_alert(latest))
        self._last_id = msg_id
        self.async_write_ha_state()
