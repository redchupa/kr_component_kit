"""Pharmacy coordinator."""
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import PHARMACY_SCAN_INTERVAL
from .api import PharmacyApiError, fetch_pharmacies

_LOGGER = logging.getLogger(__name__)


class PharmacyCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    def __init__(self, hass: HomeAssistant, api_key: str, q0: str, q1: str = "") -> None:
        super().__init__(hass, _LOGGER, name="pharmacy",
                         update_interval=timedelta(seconds=PHARMACY_SCAN_INTERVAL))
        self._api_key = api_key
        self._q0 = q0
        self._q1 = q1

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            return await fetch_pharmacies(self._api_key, self._q0, self._q1)
        except PharmacyApiError as e:
            raise UpdateFailed(str(e)) from e
        except Exception as e:  # noqa: BLE001
            raise UpdateFailed(f"약국 API 호출 실패: {e}") from e
