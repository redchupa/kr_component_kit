"""Safety Alert API client for Home Assistant integration."""

from __future__ import annotations

import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import aiohttp

from .exceptions import SafetyAlertConnectionError
from ..const import LOGGER, TZ_ASIA_SEOUL


def _make_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class SafetyAlertApiClient:
    """API client for Safety Alert integration."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the Safety Alert API client."""
        self._session: aiohttp.ClientSession = session
        self._base_url: str = (
            "https://www.safekorea.go.kr/idsiSFK/sfk/cs/sua/web/DisasterSmsList.do"
        )
        self._ssl_context = _make_ssl_context()

    async def async_get_safety_alerts(
        self,
        area_code: str = "1156000000",
        area_code2: Optional[str] = None,
        area_code3: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get safety alerts for the specified areas."""
        # Calculate date range (last 7 days) using Korea timezone
        end_date = datetime.now(TZ_ASIA_SEOUL)
        start_date = end_date - timedelta(days=7)

        # Prepare request payload with all area codes
        payload = {
            "searchInfo": {
                "firstIndex": "1",
                "rcv_Area_Id": "",
                "pageIndex": "1",
                "sbLawArea1": area_code,  # 첫 번째 지역 코드
                "dstr_se_Id": "",
                "lastIndex": "1",
                "searchBgnDe": start_date.strftime("%Y-%m-%d"),
                "searchEndDe": end_date.strftime("%Y-%m-%d"),
                "sbLawArea3": area_code3 if area_code3 else "",  # 세 번째 지역 코드
                "recordCountPerPage": "50",
                "searchWrd": "",
                "searchGb": "1",
                "c_ocrc_type": "",
                "sbLawArea2": area_code2 if area_code2 else "",  # 두 번째 지역 코드
                "pageUnit": "50",
                "pageSize": 50,
            }
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.safekorea.go.kr",
            "Referer": "https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp",
        }
        timeout = aiohttp.ClientTimeout(total=15)

        try:
            async with self._session.post(
                self._base_url,
                json=payload,
                headers=headers,
                ssl=self._ssl_context,
                timeout=timeout,
            ) as response:
                LOGGER.debug(f"Safety Alert API response status: {response.status}")

                if response.status != 200:
                    LOGGER.warning(f"Failed to get alerts: HTTP {response.status}")
                    raise SafetyAlertConnectionError(f"HTTP {response.status}")

                data = await response.json(content_type=None)
                LOGGER.debug(f"Safety Alert API response: {data}")

                return data

        except aiohttp.ClientError as e:
            LOGGER.error(f"Safety Alert API request failed: {e}")
            raise SafetyAlertConnectionError(f"Request failed: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error in Safety Alert API request: {e}")
            raise SafetyAlertConnectionError(f"Unexpected error: {e}")
