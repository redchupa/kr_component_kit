"""Pharmacy API client (data.go.kr 응급의료기관/약국 정보).

Endpoint returns XML by default. The service responds with plain-text
"Unauthorized" / "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" when the key is
wrong, so we tolerate non-XML bodies and surface a readable error
instead of letting ET.ParseError bubble up unexplained.
"""
from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import unquote
import aiohttp
from . import PHARMACY_URL

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=15)

_DAY_NAMES = {1: "월", 2: "화", 3: "수", 4: "목",
              5: "금", 6: "토", 7: "일", 8: "공휴일"}


class PharmacyApiError(Exception):
    """Raised when data.go.kr returns an auth or format error."""


def _normalize_key(api_key: str) -> str:
    """Accept either Encoding or Decoding form of the data.go.kr key.

    If it looks already URL-encoded (contains %2B / %2F / %3D), unquote
    once so aiohttp's own quoting doesn't double-encode it.
    """
    key = (api_key or "").strip()
    if "%" in key:
        key = unquote(key)
    return key


def _parse_items(text: str, q0: str, q1: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        snippet = text[:200].strip()
        raise PharmacyApiError(
            f"약국 API 응답이 XML이 아닙니다 (서비스키 또는 신청 상태 확인): {snippet}"
        ) from e

    code = root.findtext(".//resultCode") or root.findtext(".//returnReasonCode")
    msg = root.findtext(".//resultMsg") or root.findtext(".//returnAuthMsg")
    if code and code not in ("00", "0"):
        raise PharmacyApiError(f"약국 API 오류 code={code} msg={msg}")

    items = root.findall(".//item")
    if not items:
        _LOGGER.info("Pharmacy: no items for Q0=%s Q1=%s (code=%s msg=%s)",
                     q0, q1, code, msg)

    results: list[dict[str, Any]] = []
    for item in items:
        duty_time: dict[str, str] = {}
        for n in range(1, 9):
            s = item.findtext(f"dutyTime{n}s", "")
            c = item.findtext(f"dutyTime{n}c", "")
            if s or c:
                duty_time[_DAY_NAMES[n]] = f"{s}~{c}"
        results.append({
            "name": item.findtext("dutyName", ""),
            "address": item.findtext("dutyAddr", ""),
            "phone": item.findtext("dutyTel1", ""),
            "lat": item.findtext("wgs84Lat", ""),
            "lon": item.findtext("wgs84Lon", ""),
            "duty_time": duty_time,
        })
    return results


async def fetch_pharmacies(api_key: str, q0: str, q1: str = "",
                           page: int = 1, num: int = 20) -> list[dict[str, Any]]:
    """Search pharmacies. q0=시도 (e.g. 서울특별시), q1=시군구 (e.g. 강남구)."""
    q0 = (q0 or "").strip()
    q1 = (q1 or "").strip()
    params: dict[str, str] = {
        "serviceKey": _normalize_key(api_key),
        "Q0": q0,
        "ORD": "NAME",
        "pageNo": str(page),
        "numOfRows": str(num),
    }
    # Empty Q1 confuses the service; only send when set.
    if q1:
        params["Q1"] = q1

    async with aiohttp.ClientSession() as session:
        async with session.get(PHARMACY_URL, params=params, timeout=_TIMEOUT) as r:
            text = await r.text()
            if r.status != 200:
                snippet = text[:200].strip()
                raise PharmacyApiError(
                    f"약국 API HTTP {r.status} Q0={q0} Q1={q1}: {snippet}"
                )

    return _parse_items(text, q0, q1)


async def validate_pharmacy_api(api_key: str) -> bool:
    try:
        await fetch_pharmacies(api_key, "서울특별시", num=1)
        return True
    except Exception as e:  # noqa: BLE001 — config-flow validation
        _LOGGER.debug("Pharmacy validation failed: %s", e)
        return False
