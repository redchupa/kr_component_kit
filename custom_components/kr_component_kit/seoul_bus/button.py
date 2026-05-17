"""Seoul Bus refresh button — one per station."""
from __future__ import annotations
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.util import slugify
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SeoulBusRefreshButton(ButtonEntity):
    """Trigger an immediate coordinator refresh for one station.

    No-op (with a warning) when the activation switch is OFF — pressing
    the button while polling is disabled would contradict the user's
    intent for that switch.  Turn the switch on first, then press.
    """

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
            _LOGGER.warning(
                "Seoul Bus refresh for %s ignored — activation switch is OFF. "
                "Turn it on first.", self._coordinator.ars_id)
            return
        await self._coordinator.async_request_refresh()
