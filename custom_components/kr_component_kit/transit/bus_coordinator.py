"""Bus arrival coordinator using KakaoMap API."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .bus_api import fetch_stop_data, build_bus_dict

_LOGGER = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


class BusCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """One coordinator per bus stop - fetches from KakaoMap."""
    def __init__(self, hass: HomeAssistant, stop_id: str, stop_name: str) -> None:
        super().__init__(hass, _LOGGER, name=f"bus_{stop_id}",
                         update_interval=timedelta(seconds=90))
        self.stop_id = stop_id
        self.stop_name = stop_name
        self._session = async_get_clientsession(hass)
        self.last_fetched_at: datetime | None = None

    async def _async_update_data(self):
        try:
            data = await fetch_stop_data(self._session, self.stop_id)
            result = build_bus_dict(data)
            fetched_at = datetime.now(KST)
            self.last_fetched_at = fetched_at
            for line in result.values():
                arrival = line.get("arrival") or {}
                for slot, key in ((1, "arrivalTime"), (2, "arrivalTime2")):
                    secs = arrival.get(key) or 0
                    if isinstance(secs, (int, float)) and secs > 0:
                        arrival[f"_arrival_at_{slot}"] = fetched_at + timedelta(seconds=secs)
            return result
        except Exception as err:
            if self.data:
                _LOGGER.warning("Bus fetch error for %s, keeping stale data: %s",
                                self.stop_id, err)
                return self.data
            raise UpdateFailed(f"Bus API error: {err}") from err
