"""Korea Bus arrival coordinator — one per stop."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import KOREA_BUS_SCAN_INTERVAL
from .api import KoreaBusApiError, fetch_arrivals

_LOGGER = logging.getLogger(__name__)


class KoreaBusCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Polls KakaoMap busesInBusStopJson for a single stop.

    Polling is gated by `api_enabled`.  When OFF the coordinator returns
    its stale data (or an empty dict) without hitting the API, so users
    can drive polling from automations: only fetch on weekday mornings,
    only when in proximity to the stop, etc.  Same pattern as seoul_bus.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        stop_id: str,
        stop_name: str,
        include_routes: list[str] | None,
        scan_interval: int = KOREA_BUS_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass, _LOGGER,
            name=f"korea_bus_{stop_id}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.stop_id = stop_id
        self.stop_name = stop_name
        self._include_routes = set(include_routes or [])
        self._session = async_get_clientsession(hass)
        # See SeoulBusCoordinator.api_enabled — same contract.
        self.api_enabled: bool = True

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        if not self.api_enabled:
            _LOGGER.debug(
                "Korea Bus polling skipped for %s — api_enabled=False",
                self.stop_id)
            return self.data or {}
        try:
            arrivals = await fetch_arrivals(self._session, self.stop_id)
        except KoreaBusApiError as err:
            if self.data:
                _LOGGER.warning(
                    "Korea Bus fetch failed for %s, keeping stale data: %s",
                    self.stop_id, err)
                return self.data
            raise UpdateFailed(str(err)) from err

        if self._include_routes:
            return {k: v for k, v in arrivals.items() if k in self._include_routes}
        return arrivals
