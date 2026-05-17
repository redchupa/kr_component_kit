"""Seoul Bus arrival coordinator — one per station."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import SEOUL_BUS_SCAN_INTERVAL
from .api import SeoulBusApiError, build_route_dict, fetch_station

_LOGGER = logging.getLogger(__name__)


class SeoulBusCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Polls the Seoul Bus official API for a single station (ARS-ID)."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        ars_id: str,
        station_name: str,
        include_routes: list[str] | None,
    ) -> None:
        super().__init__(
            hass, _LOGGER,
            name=f"seoul_bus_{ars_id}",
            update_interval=timedelta(seconds=SEOUL_BUS_SCAN_INTERVAL),
        )
        self._api_key = api_key
        self.ars_id = ars_id
        self.station_name = station_name
        self._include_routes = list(include_routes or [])
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            items = await fetch_station(self._session, self._api_key, self.ars_id)
        except SeoulBusApiError as err:
            if self.data:
                _LOGGER.warning(
                    "Seoul Bus fetch failed for %s, keeping stale data: %s",
                    self.ars_id, err)
                return self.data
            raise UpdateFailed(str(err)) from err
        return build_route_dict(items, self._include_routes)
