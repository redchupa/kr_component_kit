"""Korea Bus refresh button — one per stop."""
from __future__ import annotations
from homeassistant.components.button import ButtonEntity
from ..const import DOMAIN


class KoreaBusRefreshButton(ButtonEntity):
    """Trigger an immediate coordinator refresh for one stop."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"
    _attr_name = "새로고침"

    def __init__(self, coordinator, device_info) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_korea_bus_{coordinator.stop_id}_refresh"
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        await self._coordinator.async_request_refresh()
