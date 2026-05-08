"""Pharmacy API client."""
from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from typing import Any
import aiohttp
from . import PHARMACY_URL

_LOGGER = logging.getLogger(__name__)

async def fetch_pharmacies(session, api_key, q0, q1="", page=1, num=20):
    """Search pharmacies by region. q0=시도, q1=시군구."""
    q0 = (q0 or "").strip()
    q1 = (q1 or "").strip()
    params = {"serviceKey": api_key, "Q0": q0, "Q1": q1,
              "ORD": "NAME", "pageNo": str(page), "numOfRows": str(num)}
    headers = {"User-Agent": "Mozilla/5.0 (kr_component_kit)"}
    async with session.get(PHARMACY_URL, params=params, headers=headers,
                           timeout=aiohttp.ClientTimeout(total=15)) as r:
        text = await r.text()
        if r.status != 200:
            _LOGGER.warning("Pharmacy HTTP %s Q0=%s Q1=%s body=%s",
                            r.status, q0, q1, text[:200])
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
        async with aiohttp.ClientSession() as s:
            r = await fetch_pharmacies(s, api_key, "서울특별시", num=1)
            return len(r) > 0
    except Exception:
        return False
