"""Seoul Bus refresh button — one per station."""
from __future__ import annotations
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.button import ButtonEntity
from homeassistant.util import slugify
from ..const import DOMAIN

from ..request_pacing import check_manual_refresh
from . import SEOUL_BUS_STATION_URL


class SeoulBusRefreshButton(ButtonEntity):
    """Request a refresh and report why polling is paused."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"
    _attr_name = "새로고침"

    def __init__(self, coordinator, device_info) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_seoul_bus_{coordinator.ars_id}_refresh"
        # Explicit entity_id matches Murianwind/seoul_bus convention so
        # existing user dashboards / automations port over unchanged.
        self.entity_id = (
            f"button.seoul_bus_{slugify(coordinator.ars_id)}_refresh"
        )
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        if not getattr(self._coordinator, "api_enabled", True):
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="polling_disabled",
            )
        check_manual_refresh(SEOUL_BUS_STATION_URL)
        await self._coordinator.async_request_refresh()
        check_manual_refresh(SEOUL_BUS_STATION_URL)
