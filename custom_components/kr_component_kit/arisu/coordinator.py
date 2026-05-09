"""Arisu coordinator."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import ARISU_SCAN_INTERVAL
from .api import ArisuApiClient

_LOGGER = logging.getLogger(__name__)


class ArisuCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, customer_number: str, customer_name: str) -> None:
        super().__init__(hass, _LOGGER, name="arisu",
                         update_interval=timedelta(seconds=ARISU_SCAN_INTERVAL))
        session = async_get_clientsession(hass)
        self.client = ArisuApiClient(session)
        self._num = customer_number
        self._name = customer_name

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_water_bill_data(self._num, self._name)
        except Exception as e:
            raise UpdateFailed(f"Arisu error: {e}") from e
