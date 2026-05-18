"""Seoul Bus binary sensors — low-floor + full-vehicle indicators.

Per route, slot 0 (next-arriving bus) only.  The slot-1 bus is more
useful as a fallback, not as the primary signal for automations.

These two sensors are the most-requested signals from the public
공공데이터 활용사례 list (휠체어/유모차 사용자 / 좌석 확보 / 다음
버스 추천).
"""
from __future__ import annotations
from typing import Any
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass, BinarySensorEntity)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from ..const import DOMAIN


class SeoulBusLowFloorSensor(CoordinatorEntity, BinarySensorEntity):
    """ON when the next bus is a low-floor (저상버스) vehicle.

    Maps to busType1 == "1" in the getStationByUidItem response.
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:wheelchair-accessibility"

    def __init__(self, coordinator, route: str, device_info) -> None:
        super().__init__(coordinator)
        self._route = route
        self._attr_unique_id = (
            f"{DOMAIN}_seoul_bus_{coordinator.ars_id}_{route}_low_floor"
        )
        self.entity_id = (
            f"binary_sensor.seoul_bus_{slugify(coordinator.ars_id)}_"
            f"{slugify(route)}_low_floor"
        )
        self._attr_name = f"{route} 저상버스"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        item = data.get(self._route)
        if not item:
            return None
        # busType1 — 0:일반, 1:저상, 2:굴절.  Treat 1 as the wheelchair-
        # accessible state; anything else is False.
        return str(item.get("busType1") or "") == "1"


class SeoulBusFullSensor(CoordinatorEntity, BinarySensorEntity):
    """ON when the next bus is at full capacity (만차).

    Maps to isFullFlag1 == "1" in the getStationByUidItem response.
    Use as an automation trigger to recommend the next bus.
    """

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:account-alert"

    def __init__(self, coordinator, route: str, device_info) -> None:
        super().__init__(coordinator)
        self._route = route
        self._attr_unique_id = (
            f"{DOMAIN}_seoul_bus_{coordinator.ars_id}_{route}_full"
        )
        self.entity_id = (
            f"binary_sensor.seoul_bus_{slugify(coordinator.ars_id)}_"
            f"{slugify(route)}_full"
        )
        self._attr_name = f"{route} 만차"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        item = data.get(self._route)
        if not item:
            return None
        return str(item.get("isFullFlag1") or "") == "1"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        item = data.get(self._route) or {}
        # Surface the congestion grade alongside the full flag for richer
        # automation conditions ("ON if 만차 OR 혼잡").
        congestion_label = {"3": "여유", "4": "보통", "5": "혼잡"}.get(
            str(item.get("congestion1") or ""), "")
        return {
            "congestion_code": item.get("congestion1") or "",
            "congestion": congestion_label,
            "passengers_aboard": item.get("rerideNum1") or "",
            "remaining_seats": item.get("remndrNmpr1") or "",
        }
