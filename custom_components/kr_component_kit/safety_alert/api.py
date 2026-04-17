"""Safety Alert API client for Home Assistant integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import aiohttp
import curl_cffi

from .exceptions import SafetyAlertConnectionError
from ..const import LOGGER, TZ_ASIA_SEOUL

_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.safekorea.go.kr",
    "Referer": "https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp",
}


class SafetyAlertApiClient:
    """API client for Safety Alert integration."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._base_url: str = (
            "https://www.safekorea.go.kr/idsiSFK/sfk/cs/sua/web/DisasterSmsList.do"
        )

    async def async_get_safety_alerts(
        self,
        area_code: str = "1156000000",
        area_code2: Optional[str] = None,
        area_code3: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get safety alerts for the specified areas."""
        end_date = datetime.now(TZ_ASIA_SEOUL)
        start_date = end_date - timedelta(days=7)

        payload = {
            "searchInfo": {
                "firstIndex": "1",
                "rcv_Area_Id": "",
                "pageIndex": "1",
                "sbLawArea1": area_code,
                "dstr_se_Id": "",
                "lastIndex": "1",
                "searchBgnDe": start_date.strftime("%Y-%m-%d"),
                "searchEndDe": end_date.strftime("%Y-%m-%d"),
                "sbLawArea3": area_code3 if area_code3 else "",
                "recordCountPerPage": "50",
                "searchWrd": "",
                "searchGb": "1",
                "c_ocrc_type": "",
                "sbLawArea2": area_code2 if area_code2 else "",
                "pageUnit": "50",
                "pageSize": 50,
            }
        }

        try:
            async with curl_cffi.AsyncSession(impersonate="chrome120") as session:
                response = await session.post(
                    self._base_url,
                    json=payload,
                    headers=_HEADERS,
                    verify=False,
                    timeout=15,
                )
                LOGGER.debug("Safety Alert API response status: %s", response.status_code)

                if response.status_code != 200:
                    raise SafetyAlertConnectionError(f"HTTP {response.status_code}")

                text = response.text
                if not text.strip() or text.strip().startswith("<"):
                    LOGGER.error("Safety Alert API returned non-JSON response: %s", text[:200])
                    raise SafetyAlertConnectionError("Non-JSON response from API")

                data = response.json()
                LOGGER.debug("Safety Alert API response parsed successfully")
                return data

        except SafetyAlertConnectionError:
            raise
        except Exception as e:
            LOGGER.error("Safety Alert API request failed: %s", e)
            raise SafetyAlertConnectionError(f"Request failed: {e}")
