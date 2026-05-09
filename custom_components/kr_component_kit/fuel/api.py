"""Opinet fuel price API client."""
from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from typing import Any
import aiohttp
from . import OPINET_AVG_URL, OPINET_LOWPRICE_URL

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=15)


class OpinetApiError(Exception):
    """Raised when Opinet returns an error status / RESULT.CODE / unparseable body."""


def _parse_xml(text: str) -> ET.Element:
    """Parse XML, raising OpinetApiError with snippet on failure."""
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        snippet = text[:200].strip()
        raise OpinetApiError(
            f"Opinet 응답이 XML이 아닙니다 (서비스 키 확인): {snippet}"
        ) from e


def _check_result(root: ET.Element) -> None:
    """Raise OpinetApiError if Opinet returned an error code (anything other than '00').

    Opinet wraps errors as <RESULT><CODE>F</CODE><MESSAGE>...</MESSAGE></RESULT>.
    Successful responses use code "00" (or no RESULT element on legacy endpoints).
    """
    code = root.findtext(".//RESULT/CODE")
    if code and code != "00":
        msg = root.findtext(".//RESULT/MESSAGE", "")
        raise OpinetApiError(f"Opinet code={code} msg={msg}")


async def validate_opinet(api_key: str) -> bool:
    """Probe the Opinet service key. Returns True only when CODE='00'."""
    params = {"code": api_key, "out": "xml"}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(OPINET_AVG_URL, params=params, timeout=_TIMEOUT) as r:
                if r.status != 200:
                    return False
                text = await r.text()
        root = _parse_xml(text)
        _check_result(root)
        return True
    except (OpinetApiError, aiohttp.ClientError, Exception) as e:  # noqa: BLE001
        _LOGGER.debug("Opinet validation failed: %s", e)
        return False


async def fetch_avg_price(session: aiohttp.ClientSession,
                           api_key: str) -> list[dict[str, str]]:
    params = {"code": api_key, "out": "xml"}
    async with session.get(OPINET_AVG_URL, params=params, timeout=_TIMEOUT) as r:
        text = await r.text()
        status = r.status
    if status != 200:
        snippet = text[:200].strip()
        raise OpinetApiError(f"Opinet HTTP {status}: {snippet}")
    root = _parse_xml(text)
    _check_result(root)
    results = []
    for oil in root.findall(".//OIL"):
        results.append({
            "product_code": oil.findtext("PRODCD", ""),
            "price": oil.findtext("PRICE", ""),
            "diff": oil.findtext("DIFF", ""),
        })
    return results


async def fetch_low_price(session: aiohttp.ClientSession, api_key: str,
                           sido_code: str, fuel_code: str) -> list[dict[str, Any]]:
    params = {"code": api_key, "out": "xml", "sido": sido_code, "prodcd": fuel_code, "cnt": "5"}
    async with session.get(OPINET_LOWPRICE_URL, params=params, timeout=_TIMEOUT) as r:
        text = await r.text()
        status = r.status
    if status != 200:
        snippet = text[:200].strip()
        raise OpinetApiError(f"Opinet HTTP {status}: {snippet}")
    root = _parse_xml(text)
    _check_result(root)
    results = []
    for oil in root.findall(".//OIL"):
        results.append({
            "station_name": oil.findtext("OS_NM", ""),
            "price": oil.findtext("PRICE", ""),
            "address": oil.findtext("NEW_ADR", "") or oil.findtext("VAN_ADR", ""),
            "brand": oil.findtext("POLL_DIV_CD", ""),
        })
    return results
