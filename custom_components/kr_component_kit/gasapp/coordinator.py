"""GasApp coordinator."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import GASAPP_SCAN_INTERVAL
from .api import GasAppApiClient

_LOGGER = logging.getLogger(__name__)


class GasAppCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, token: str, member_id: str, contract_num: str) -> None:
        super().__init__(hass, _LOGGER, name="gasapp",
                         update_interval=timedelta(seconds=GASAPP_SCAN_INTERVAL))
        session = async_get_clientsession(hass)
        self.client = GasAppApiClient(session)
        self.client.set_credentials(token, member_id, contract_num)
        self._contract_num = contract_num

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            home = await self.client.async_get_home_data()
            bill = await self.client.async_get_current_bill()
            return {"home_data": home, "current_bill": bill}
        except Exception as e:
            raise UpdateFailed(f"GasApp error: {e}") from e
