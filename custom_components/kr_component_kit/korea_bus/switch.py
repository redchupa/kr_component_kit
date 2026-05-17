"""Korea Bus API-activation switch — one per stop.

See seoul_bus/switch.py for the design rationale.  Same gate-by-switch
contract, applied to the KakaoMap-backed Korea Bus flow.
"""
from __future__ import annotations
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import slugify
from ..const import DOMAIN


class KoreaBusActiveSwitch(SwitchEntity, RestoreEntity):
    """Gate flag for the coordinator's polling loop."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:api"
    _attr_name = "업데이트 활성화"

    def __init__(self, coordinator, device_info) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = (
            f"{DOMAIN}_korea_bus_{coordinator.stop_id}_api_active"
        )
        self.entity_id = (
            f"switch.korea_bus_{slugify(coordinator.stop_id)}_api_active"
        )
        self._attr_device_info = device_info
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
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
