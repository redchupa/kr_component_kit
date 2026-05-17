"""Seoul Bus official API (ws.bus.go.kr/api/rest/stationinfo/getStationByUid).

The endpoint returns XML.  The route number the user sees on the bus is `rtNm`
(e.g. "2230"), and the internal id is `busRouteId` (e.g. "100100203").  We key
everything in this module by `rtNm` because that is what the user types into
the config flow.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any
import aiohttp
import xmltodict
from . import SEOUL_BUS_STATION_URL

_LOGGER = logging.getLogger(__name__)


class SeoulBusApiError(Exception):
    """Raised when the Seoul Bus API returns an error or unparseable body."""


def _mask(key: str) -> str:
    return f"{key[:4]}…" if key else "(empty)"


async def fetch_station(
    session: aiohttp.ClientSession, api_key: str, ars_id: str,
) -> list[dict[str, Any]]:
    """Fetch the list of bus items at a station.

    Returns a list of itemList dicts as parsed by xmltodict.  Raises
    `SeoulBusApiError` on transport failure or server-side errors so callers
    can distinguish from a successful empty response (no buses currently).
    """
    url = SEOUL_BUS_STATION_URL.format(key=api_key, ars_id=ars_id)
    try:
        async with asyncio.timeout(15):
            async with session.get(url) as r:
                body = await r.text()
    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        raise SeoulBusApiError(
            f"Seoul Bus API transport error for arsId={ars_id} key={_mask(api_key)}: {e}"
        ) from e

    try:
        data = xmltodict.parse(body)
    except Exception as e:  # xmltodict raises ExpatError / ValueError variants
        raise SeoulBusApiError(
            f"Seoul Bus API returned non-XML body for arsId={ars_id}: {e}"
        ) from e

    result = (data or {}).get("ServiceResult") or {}
    header = result.get("comMsgHeader") or {}
    err_code = header.get("errMsg")
    # Successful responses use errMsg = "정상적으로 처리되었습니다." (or absent).
    # 4* / 5* responses carry the failure here.
    if err_code and err_code not in ("정상적으로 처리되었습니다.", None):
        raise SeoulBusApiError(
            f"Seoul Bus API error for arsId={ars_id}: {err_code}"
        )

    items = (result.get("msgBody") or {}).get("itemList", [])
    if items is None:
        return []
    if not isinstance(items, list):
        items = [items]
    return items


def build_route_dict(
    items: list[dict[str, Any]],
    include_routes: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Index items by route number (`rtNm`).

    `include_routes`, when non-empty, restricts to those route numbers.  We
    intentionally match by `rtNm` (the user-visible route number, e.g. "2230")
    not `busRouteId` — see module docstring.
    """
    out: dict[str, dict[str, Any]] = {}
    targets = {r.strip() for r in (include_routes or []) if r.strip()}
    for item in items:
        rt = item.get("rtNm")
        if not rt:
            continue
        if targets and rt not in targets:
            continue
        out[rt] = item
    return out


def build_route_labels(items: list[dict[str, Any]]) -> dict[str, str]:
    """Build {rtNm: label} for multi-select pickers in the config flow."""
    labels: dict[str, str] = {}
    for item in items:
        rt = item.get("rtNm")
        if not rt:
            continue
        # busRouteAbrv is sometimes empty; nxtStn / stationNm gives context.
        next_stop = item.get("nxtStn") or item.get("stationNm") or ""
        labels[rt] = f"{rt} (→ {next_stop})" if next_stop else rt
    # Stable ordering — numeric first, then alpha.
    return dict(sorted(labels.items(), key=lambda kv: (
        not kv[0].isdigit(), int(kv[0]) if kv[0].isdigit() else kv[0])))


async def validate_api_key(
    session: aiohttp.ClientSession, api_key: str, sample_ars: str = "23288",
) -> bool:
    """Probe API key with a known-valid ARS-ID (default: 사당역 정류장).

    Returns True if the API accepts the key (any non-error response).  We
    don't require the station to actually have buses — we just want to know
    that auth passed.
    """
    try:
        await fetch_station(session, api_key, sample_ars)
        return True
    except SeoulBusApiError as e:
        _LOGGER.warning("Seoul Bus API key validation failed: %s", e)
        return False
