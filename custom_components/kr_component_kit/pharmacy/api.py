"""Pharmacy API client."""
from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import curl_cffi
from . import PHARMACY_URL

_LOGGER = logging.getLogger(__name__)

_HEADERS = {
    "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def fetch_pharmacies(api_key, q0, q1="", page=1, num=20):
    """Search pharmacies by region. q0=시도, q1=시군구."""
    q0 = (q0 or "").strip()
    q1 = (q1 or "").strip()
    # Accept either Encoding or Decoding form of the data.go.kr service key.
    # If it looks already URL-encoded (e.g. contains %2B, %2F, %3D), unquote
    # once so curl_cffi's own quoting doesn't double-encode it.
    key = (api_key or "").strip()
    if "%" in key:
        key = unquote(key)
    params = {"serviceKey": key, "Q0": q0, "Q1": q1,
              "ORD": "NAME", "pageNo": str(page), "numOfRows": str(num)}
    async with curl_cffi.AsyncSession(impersonate="chrome120") as session:
        r = await session.get(PHARMACY_URL, params=params,
                               headers=_HEADERS, verify=False, timeout=15)
        text = r.text
        if r.status_code != 200:
            _LOGGER.warning("Pharmacy HTTP %s Q0=%s Q1=%s body=%s",
                            r.status_code, q0, q1, text[:200])
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        _LOGGER.error("Pharmacy XML parse failed (Q0=%s Q1=%s): %s | body=%s",
                      q0, q1, e, text[:500])
        raise
    code = root.findtext(".//resultCode") or root.findtext(".//returnReasonCode")
    msg = root.findtext(".//resultMsg") or root.findtext(".//returnAuthMsg")
    if code and code not in ("00", "0"):
        _LOGGER.warning("Pharmacy API error Q0=%s Q1=%s code=%s msg=%s | body=%s",
                        q0, q1, code, msg, text[:500])
    items = root.findall(".//item")
    if not items:
        _LOGGER.info("Pharmacy no items Q0=%s Q1=%s code=%s msg=%s",
                     q0, q1, code, msg)
    results = []
    for item in items:
        duty_time = {}
        for day_n in range(1, 9):  # dutyTime1~8 (월~일+공휴일)
            s = item.findtext(f"dutyTime{day_n}s", "")
            c = item.findtext(f"dutyTime{day_n}c", "")
            if s or c:
                day_names = {1:"월",2:"화",3:"수",4:"목",5:"금",6:"토",7:"일",8:"공휴일"}
                duty_time[day_names.get(day_n, str(day_n))] = f"{s}~{c}"
        results.append({
            "name": item.findtext("dutyName", ""),
            "address": item.findtext("dutyAddr", ""),
            "phone": item.findtext("dutyTel1", ""),
            "lat": item.findtext("wgs84Lat", ""),
            "lon": item.findtext("wgs84Lon", ""),
            "duty_time": duty_time,
        })
    return results


async def validate_pharmacy_api(api_key):
    try:
        r = await fetch_pharmacies(api_key, "서울특별시", num=1)
        return len(r) > 0
    except Exception:
        return False
