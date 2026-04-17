"""Safety Alert Region API client for getting region codes."""

from __future__ import annotations

from typing import Dict, List

import aiohttp

from ..const import LOGGER

_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)
_MAIN_URL = "https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp"
_BASE_URL = "https://www.safekorea.go.kr/idsiSFK/sfk/cs/sua/web"
_BASE_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.safekorea.go.kr",
    "Referer": _MAIN_URL,
}

# 전국 17개 시도 — 행정구역이므로 하드코딩
_SIDO_LIST = [
    {"code": "1100000000", "name": "서울특별시"},
    {"code": "2600000000", "name": "부산광역시"},
    {"code": "2700000000", "name": "대구광역시"},
    {"code": "2800000000", "name": "인천광역시"},
    {"code": "2900000000", "name": "광주광역시"},
    {"code": "3000000000", "name": "대전광역시"},
    {"code": "3100000000", "name": "울산광역시"},
    {"code": "3600000000", "name": "세종특별자치시"},
    {"code": "4100000000", "name": "경기도"},
    {"code": "4200000000", "name": "강원특별자치도"},
    {"code": "4300000000", "name": "충청북도"},
    {"code": "4400000000", "name": "충청남도"},
    {"code": "4500000000", "name": "전북특별자치도"},
    {"code": "4600000000", "name": "전라남도"},
    {"code": "4700000000", "name": "경상북도"},
    {"code": "4800000000", "name": "경상남도"},
    {"code": "5000000000", "name": "제주특별자치도"},
]


class SafetyAlertRegionApiClient:
    """API client for Safety Alert region code retrieval."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session: aiohttp.ClientSession = session

    async def _init_session(self) -> None:
        """Visit main page to obtain session cookies before API calls."""
        try:
            async with self._session.get(
                _MAIN_URL,
                headers={
                    "User-Agent": _BASE_HEADERS["User-Agent"],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                ssl=False,
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                LOGGER.debug("Session init status: %s", response.status)
        except Exception as e:
            LOGGER.warning("Session init failed (continuing anyway): %s", e)

    async def async_get_sido_list(self) -> List[Dict[str, str]]:
        """Return hardcoded list of sido (시도) regions."""
        return _SIDO_LIST

    async def async_get_sgg_list(self, sido_code: str) -> List[Dict[str, str]]:
        """Get list of sgg (시군구) regions for a given sido."""
        await self._init_session()
        url = f"{_BASE_URL}/Get_CBS_Sgg_List.do"
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
                text = await response.text()
                LOGGER.debug("Sgg list raw response: %s", text[:200])
                if not text.strip() or text.strip().startswith("<"):
                    LOGGER.warning("Sgg list API returned non-JSON response")
                    return []
                import json as json_mod
                data = json_mod.loads(text)
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
        await self._init_session()
        url = f"{_BASE_URL}/Get_CBS_Emd_List.do"
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
                text = await response.text()
                LOGGER.debug("Emd list raw response: %s", text[:200])
                if not text.strip() or text.strip().startswith("<"):
                    LOGGER.warning("Emd list API returned non-JSON response")
                    return []
                import json as json_mod
                data = json_mod.loads(text)
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
