"""Kakao Bus arrival coordinator — one per stop."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import KAKAO_BUS_SCAN_INTERVAL
from .api import KakaoBusApiError, fetch_arrivals

_LOGGER = logging.getLogger(__name__)


class KakaoBusCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Polls KakaoMap busesInBusStopJson for a single stop."""

    def __init__(
        self,
        hass: HomeAssistant,
        stop_id: str,
        stop_name: str,
        include_routes: list[str] | None,
        scan_interval: int = KAKAO_BUS_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass, _LOGGER,
            name=f"kakao_bus_{stop_id}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.stop_id = stop_id
        self.stop_name = stop_name
        self._include_routes = set(include_routes or [])
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            arrivals = await fetch_arrivals(self._session, self.stop_id)
        except KakaoBusApiError as err:
            if self.data:
                _LOGGER.warning(
                    "Kakao Bus fetch failed for %s, keeping stale data: %s",
                    self.stop_id, err)
                return self.data
            raise UpdateFailed(str(err)) from err

        if self._include_routes:
            return {k: v for k, v in arrivals.items() if k in self._include_routes}
        return arrivals
