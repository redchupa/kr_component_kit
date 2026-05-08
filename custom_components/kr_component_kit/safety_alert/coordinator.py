"""Safety Alert coordinator."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import SAFETY_ALERT_SCAN_INTERVAL
from .api import SafetyAlertApiClient
from .exceptions import SafetyAlertConnectionError, SafetyAlertDataError
from ..utils import TZ_ASIA_SEOUL

_LOGGER = logging.getLogger(__name__)


class SafetyAlertCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for a single 안전알림 region."""

    def __init__(
        self,
        hass: HomeAssistant,
        area_code: str,
        area_code2: Optional[str] = None,
        area_code3: Optional[str] = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"safety_alert_{area_code}",
            update_interval=timedelta(seconds=SAFETY_ALERT_SCAN_INTERVAL),
        )
        self._area_code = area_code
        self._area_code2 = area_code2 or None
        self._area_code3 = area_code3 or None
        self._client = SafetyAlertApiClient()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            result = await self._client.async_get_safety_alerts(
                self._area_code, self._area_code2, self._area_code3
            )
        except (SafetyAlertConnectionError, SafetyAlertDataError) as err:
            raise UpdateFailed(f"Safety Alert API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        alerts = result.get("disasterSmsList", []) or []
        count = result.get("rtnResult", {}).get("totCnt", len(alerts))
        return {
            "has_data": bool(alerts),
            "metadata": {"count": count},
            "parsed_data": {"data": alerts},
            "last_updated": datetime.now(TZ_ASIA_SEOUL).isoformat(),
        }
