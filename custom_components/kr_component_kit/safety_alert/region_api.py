"""Safety Alert Region API client for getting region codes."""

from __future__ import annotations

from typing import Dict, List

import aiohttp

from ..const import LOGGER

_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)
_BASE_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.safekorea.go.kr",
    "Referer": "https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp",
}


class SafetyAlertRegionApiClient:
    """API client for Safety Alert region code retrieval."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the Safety Alert Region API client."""
        self._session: aiohttp.ClientSession = session
        self._base_url: str = "https://www.safekorea.go.kr/idsiSFK/sfk/cs/sua/web"

    async def async_get_sido_list(self) -> List[Dict[str, str]]:
        """Get list of sido (시도) regions."""
        import json as json_mod
        url = f"{self._base_url}/Get_CBS_Sido_List.do"
        try:
            async with self._session.post(
                url,
                json={"sido_searchInfo": {}},
                headers=_BASE_HEADERS,
                ssl=False,
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    LOGGER.error("Sido list API request failed with status: %s", response.status)
                    return []
                text = await response.text()
                LOGGER.debug("Sido list raw response: %s", text[:500])
                if not text.strip():
                    LOGGER.error("Sido list API returned empty response")
                    return []
                try:
                    data = json_mod.loads(text)
                except json_mod.JSONDecodeError as e:
                    LOGGER.error("Sido list JSON parse failed: %s | body: %s", e, text[:200])
                    raise
                sido_list = data.get("cbs_sido_list", [])
                result = [
                    {
                        "code": sido.get("BDONG_CD", ""),
                        "name": sido.get("CBS_AREA_NM", ""),
                        "id": sido.get("CBS_AREA_ID", ""),
                    }
                    for sido in sido_list
                ]
                result.sort(key=lambda x: x["name"])
                return result
        except Exception as e:
            LOGGER.error("Sido list API request failed: %s", e)
            raise

    async def async_get_sgg_list(self, sido_code: str) -> List[Dict[str, str]]:
        """Get list of sgg (시군구) regions for a given sido."""
        url = f"{self._base_url}/Get_CBS_Sgg_List.do"
        payload = {"sgg_searchInfo": {"BDONG_CD": "", "bdong_cd": sido_code}}
        try:
            async with self._session.post(
                url,
                json=payload,
                headers=_BASE_HEADERS,
                ssl=False,
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    LOGGER.warning("Sgg list API request failed with status: %s", response.status)
                    return []
                data = await response.json(content_type=None)
                sgg_list = data.get("cbs_sgg_list", [])
                result = [
                    {
                        "code": sgg.get("BDONG_CD", ""),
                        "name": sgg.get("CBS_AREA_NM", ""),
                    }
                    for sgg in sgg_list
                ]
                result.sort(key=lambda x: x["name"])
                return result
        except Exception as e:
            LOGGER.warning("Sgg list API request failed: %s", e)
            raise

    async def async_get_emd_list(self, sido_code: str, sgg_code: str) -> List[Dict[str, str]]:
        """Get list of emd (읍면동) regions for a given sido and sgg."""
        url = f"{self._base_url}/Get_CBS_Emd_List.do"
        payload = {
            "emd_searchInfo": {
                "BDONG_CD": "",
                "area1_bdong_cd": sido_code,
                "area2_bdong_cd": sgg_code,
            }
        }
        try:
            async with self._session.post(
                url,
                json=payload,
                headers=_BASE_HEADERS,
                ssl=False,
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    LOGGER.warning("Emd list API request failed with status: %s", response.status)
                    return []
                data = await response.json(content_type=None)
                emd_list = data.get("cbs_emd_list", [])
                result = [
                    {
                        "code": emd.get("BDONG_CD", ""),
                        "name": emd.get("CBS_AREA_NM", ""),
                    }
                    for emd in emd_list
                ]
                result.sort(key=lambda x: x["name"])
                return result
        except Exception as e:
            LOGGER.warning("Emd list API request failed: %s", e)
            raise
