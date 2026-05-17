"""KakaoMap mobile bus API helpers.

Three operations:
- search_stops(name) → HTML scrape of searchView (used only in config flow)
- fetch_stop_routes(stop_id) → HTML scrape of busStationInfo (config flow only)
- fetch_arrivals(stop_id) → JSON busesInBusStopJson (coordinator runtime)

All three rely on KakaoMap's mobile site.  When the HTML/JSON layout changes,
fixes only need to land in this module.
"""
from __future__ import annotations
import asyncio
import html
import logging
import re
import urllib.parse
from typing import Any
import aiohttp
from bs4 import BeautifulSoup
from . import KAKAO_ARRIVALS_URL, KAKAO_HEADERS, KAKAO_SEARCH_URL, KAKAO_STATION_URL

_LOGGER = logging.getLogger(__name__)


class KakaoBusApiError(Exception):
    """Raised on transport, HTTP, or parse failures."""


def _arrival_headers(stop_id: str) -> dict[str, str]:
    return {**KAKAO_HEADERS,
            "Referer": f"{KAKAO_ARRIVALS_URL}?busStopId={stop_id}",
            "X-Requested-With": "XMLHttpRequest"}


async def search_stops(
    session: aiohttp.ClientSession, name: str,
) -> dict[str, dict[str, Any]]:
    """Search bus stops by name.  Returns {stop_id: stop_info}.

    `stop_info` keys: stop_number, direction, location, bus_types, title.
    """
    url = f"{KAKAO_SEARCH_URL}?q={urllib.parse.quote(name)}&lvl=2#!/all/list/bus"
    try:
        async with asyncio.timeout(10):
            async with session.get(url, headers=KAKAO_HEADERS) as r:
                if r.status != 200:
                    raise KakaoBusApiError(
                        f"KakaoMap search HTTP {r.status} for q={name!r}")
                body = await r.text()
    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        raise KakaoBusApiError(f"KakaoMap search transport error: {e}") from e

    soup = BeautifulSoup(body, "html.parser")
    results: dict[str, dict[str, Any]] = {}
    for stop in soup.find_all("li", class_="search_item"):
        data_id = stop.get("data-id")
        # HTML entity-encoded values (예: 정류장 이름의 &) 까지 안전하게 처리.
        data_title = html.unescape(stop.get("data-title") or "")
        if not data_id:
            continue

        stop_number_el = stop.find(
            "span", class_="screen_out", string="버스 정류장 번호 : ")
        stop_number = (
            stop_number_el.next_sibling.strip()
            if stop_number_el and isinstance(stop_number_el.next_sibling, str)
            else None
        )

        direction_el = stop.find("span", class_="txt_bar")
        direction = (
            direction_el.next_sibling.strip()
            if direction_el and isinstance(direction_el.next_sibling, str)
            else None
        )

        ginfo = stop.find("span", class_="txt_ginfo")
        location = ginfo.get_text(strip=True) if ginfo else ""
        bus_types = [
            bt.get_text(strip=True)
            for bt in stop.find_all(
                "span", class_=lambda x: x and x.startswith("bus_type"))
        ]

        if stop_number and direction:
            results[data_id] = {
                "stop_number": stop_number,
                "direction": direction,
                "location": location,
                "bus_types": bus_types,
                "title": f"{data_title}({stop_number}) - {direction}",
            }
    return results


async def fetch_stop_routes(
    session: aiohttp.ClientSession, stop_id: str,
) -> list[dict[str, str]]:
    """Fetch the route list at a stop (config flow only).

    Returns [{"number", "type"}, ...] for use in a multi-select.
    """
    url = f"{KAKAO_STATION_URL}?busStopId={stop_id}"
    try:
        async with asyncio.timeout(10):
            async with session.get(url, headers=KAKAO_HEADERS) as r:
                if r.status != 200:
                    raise KakaoBusApiError(
                        f"KakaoMap stationInfo HTTP {r.status} for stop={stop_id}")
                body = await r.text()
    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        raise KakaoBusApiError(
            f"KakaoMap stationInfo transport error for stop={stop_id}: {e}") from e

    soup = BeautifulSoup(body, "html.parser")
    routes: list[dict[str, str]] = []
    seen: set[str] = set()
    for bus in soup.find_all("li", attrs={"data-id": True}):
        num_el = bus.find("strong", class_="tit_g")
        if not num_el:
            continue
        number = num_el.get_text(strip=True)
        if not number or number in seen:
            continue
        seen.add(number)
        type_el = bus.find("span", class_=re.compile("bus_type.*"))
        bus_type = type_el.get_text(strip=True) if type_el else ""
        routes.append({"number": number, "type": bus_type})
    return routes


async def fetch_arrivals(
    session: aiohttp.ClientSession, stop_id: str,
) -> dict[str, dict[str, Any]]:
    """Runtime poll — fetch real-time arrivals.  Returns {route_name: bus_info}.

    Used by the coordinator at every scan interval.
    """
    url = f"{KAKAO_ARRIVALS_URL}?busStopId={stop_id}"
    headers = _arrival_headers(stop_id)
    try:
        async with asyncio.timeout(10):
            async with session.get(url, headers=headers) as r:
                if r.status != 200:
                    raise KakaoBusApiError(
                        f"KakaoMap arrivals HTTP {r.status} for stop={stop_id}")
                data = await r.json(content_type=None)
    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        raise KakaoBusApiError(
            f"KakaoMap arrivals transport error for stop={stop_id}: {e}") from e
    except ValueError as e:
        raise KakaoBusApiError(
            f"KakaoMap arrivals returned non-JSON for stop={stop_id}: {e}") from e

    items = (data or {}).get("busesList") or []
    return {b.get("name"): b for b in items if b.get("name")}
