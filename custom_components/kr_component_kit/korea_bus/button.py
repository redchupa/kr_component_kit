"""Korea Bus refresh button — one per stop."""
from __future__ import annotations
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.util import slugify
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class KoreaBusRefreshButton(ButtonEntity):
    """Trigger an immediate coordinator refresh for one stop.

    No-op (with a warning) when the activation switch is OFF — see
    seoul_bus/button.py for the rationale.
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"
    _attr_name = "새로고침"

    def __init__(self, coordinator, device_info) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_korea_bus_{coordinator.stop_id}_refresh"
        self.entity_id = (
            f"button.korea_bus_{slugify(coordinator.stop_id)}_refresh"
        )
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        if not getattr(self._coordinator, "api_enabled", True):
            _LOGGER.warning(
                "Korea Bus refresh for %s ignored — activation switch is OFF. "
                "Turn it on first.", self._coordinator.stop_id)
            return
        await self._coordinator.async_request_refresh()
