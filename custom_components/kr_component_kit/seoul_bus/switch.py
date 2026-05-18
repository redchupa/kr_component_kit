"""Seoul Bus API-activation switch — one per station.

ON  → coordinator polls at every scan interval (default 60s).
OFF → coordinator returns stale data without hitting the API.

The point is to let users drive polling from HA automations — only
fetch on weekday mornings, only when within a certain distance of the
stop, only during a calendar event, etc.  Pattern inherited from the
upstream Murianwind/seoul_bus fork.
"""
from __future__ import annotations
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import slugify
from ..const import DOMAIN


class SeoulBusActiveSwitch(SwitchEntity, RestoreEntity):
    """Gate flag for the coordinator's polling loop."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:api"
    _attr_name = "업데이트 활성화"

    def __init__(self, coordinator, device_info) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = (
            f"{DOMAIN}_seoul_bus_{coordinator.ars_id}_api_active"
        )
        # Explicit entity_id keeps automations portable — matches the entity
        # ID convention shipped by Murianwind/seoul_bus so existing user
        # automations from that fork keep working unchanged.
        self.entity_id = (
            f"switch.seoul_bus_{slugify(coordinator.ars_id)}_api_active"
        )
        self._attr_device_info = device_info
        # Default ON for fresh installs — users expect data immediately
        # after registering a stop, not after hunting for a hidden
        # switch.  RestoreEntity will overwrite from the last saved
        # state on async_added_to_hass, so users who deliberately turned
        # it OFF before a restart get their preference back.
        self._attr_is_on = True

    async def async_added_to_hass(self) -> None:
        """Restore last on/off state and sync coordinator flag."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"
        self._coordinator.api_enabled = self._attr_is_on

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self._coordinator.api_enabled = True
        self.async_write_ha_state()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self._coordinator.api_enabled = False
        self.async_write_ha_state()
