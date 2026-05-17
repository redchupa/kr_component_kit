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


def normalize_ars_id(raw: str) -> str | None:
    """Normalize a user-entered ARS-ID.

    Returns the 5-digit ARS-ID on success, or None when the input cannot
    be coerced (non-numeric or longer than 5 digits — e.g. a KakaoMap
    `busStopId` mistakenly pasted into the Seoul Bus flow).

    Leading zeros are added when the user types something like "1234"
    for ARS-ID "01234" — the Seoul Bus API is strict about the exact
    5-character form.
    """
    if raw is None:
        return None
    cleaned = raw.strip()
    if not cleaned.isdigit():
        return None
    if len(cleaned) > 5:
        return None
    return cleaned.zfill(5)


# headerCd values per the official 정류소정보조회 활용가이드 §다.오류코드안내.
# 0  = 정상적으로 처리되었습니다
# 1  = 시스템 오류
# 2  = 잘못된 쿼리 (parameter validation)
# 3  = 정류소를 찾을 수 없습니다 (ARS-ID does not exist in the Seoul DB)
# 4  = 노선을 찾을 수 없습니다
# 5  = 잘못된 위치
# 6  = 실시간 정보 일시 불가
# 7  = 경로 검색 결과 없음
# 8  = 운행 종료
# Auth / quota / inactive-key failures usually come through codes 1, 2, or
# via data.go.kr's outer envelope (SERVICE_KEY_IS_NOT_REGISTERED_ERROR etc.)
# inside `comMsgHeader`, which is a separate path the parser also handles.
_HEADER_STOP_NOT_FOUND = "3"


def _parse_header(result: dict[str, Any]) -> tuple[str, str]:
    """Return (header_code, header_message) from a getStationByUid response.

    The 정류소정보조회 service puts its real status in `msgHeader.headerCd` +
    `msgHeader.headerMsg`.  An earlier comment in this module thought the
    code was in `comMsgHeader.errMsg`; that was wrong and is why valid
    ARS-IDs were silently returning empty lists.

    `comMsgHeader.returnReasonCode` / `errMsg` is only populated when the
    outer data.go.kr API gateway rejects the request before it reaches the
    Seoul backend (e.g. an unregistered or inactive service key).  We
    surface that too via the same return tuple.
    """
    msg_header = result.get("msgHeader") or {}
    code = str(msg_header.get("headerCd") or "").strip()
    message = (msg_header.get("headerMsg") or "").strip()
    # Outer envelope (data.go.kr gateway).  When the gateway rejects the
    # call there's typically no msgHeader at all.
    if not code:
        com = result.get("comMsgHeader") or {}
        # data.go.kr conventionally fills `returnReasonCode` (numeric) and
        # `errMsg` (text) here when the key/quota fails.
        code = str(com.get("returnReasonCode") or "").strip()
        message = (com.get("errMsg") or "").strip() or message
    return code, message


async def fetch_station(
    session: aiohttp.ClientSession, api_key: str, ars_id: str,
) -> list[dict[str, Any]]:
    """Fetch the list of bus items at a station.

    Returns a list of itemList dicts.  Raises `SeoulBusApiError` on
    transport failures, parse failures, or server-side failures other than
    "stop not found" (headerCd != "0" and != "3").  A "3 정류소를 찾을 수
    없습니다" response is folded into an empty list so callers can treat it
    as "no matching stop" without exception handling.
    """
    url = SEOUL_BUS_STATION_URL.format(key=api_key, ars_id=ars_id)
    try:
        async with asyncio.timeout(15):
            async with session.get(url) as r:
                body = await r.text()
    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        raise SeoulBusApiError(
            f"Seoul Bus API transport error for arsId={ars_id} "
            f"key={_mask(api_key)}: {e}"
        ) from e

    try:
        data = xmltodict.parse(body)
    except Exception as e:  # xmltodict raises ExpatError / ValueError variants
        raise SeoulBusApiError(
            f"Seoul Bus API returned non-XML body for arsId={ars_id}: {e}"
        ) from e

    result = (data or {}).get("ServiceResult") or {}
    code, message = _parse_header(result)

    if code and code != "0":
        if code == _HEADER_STOP_NOT_FOUND:
            # Surface as "no items" — callers want the same "정류장을
            # 찾을 수 없습니다" UX as a genuine empty body would give.
            _LOGGER.debug(
                "Seoul Bus API: headerCd=3 (stop not found) for arsId=%s",
                ars_id)
            return []
        raise SeoulBusApiError(
            f"Seoul Bus API headerCd={code} for arsId={ars_id}: "
            f"{message or '(no message)'}"
        )

    items = (result.get("msgBody") or {}).get("itemList", [])
    if items is None:
        _LOGGER.debug(
            "Seoul Bus API returned headerCd=%r but empty itemList for "
            "arsId=%s — treating as no items.", code or "(absent)", ars_id)
        return []
    if not isinstance(items, list):
        items = [items]
    if not items:
        _LOGGER.debug(
            "Seoul Bus API returned 0 items for arsId=%s (headerCd=%r, "
            "msg=%r).", ars_id, code or "(absent)", message)
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
    session: aiohttp.ClientSession, api_key: str,
) -> str | None:
    """Probe the API with the given key. Returns None on success, or one of
    `"invalid_api_key"` / `"cannot_connect"` on failure.

    Strategy: call fetch_station() with a known-real Seoul ARS-ID (`23288`,
    사당역 stop).  A valid registered key returns headerCd 0 (success).
    Code 3 (stop not found) also indicates the key reached the backend
    successfully, so we treat that as valid too.  Anything else — auth
    keywords, gateway envelope errors, transport failures — is bucketed
    into one of two user-facing reasons.
    """
    try:
        await fetch_station(session, api_key, "23288")
        return None
    except SeoulBusApiError as e:
        msg = str(e).upper()
        # data.go.kr gateway-class rejections (key never reached the
        # Seoul backend).  The portal sometimes takes up to ~1h to
        # activate a freshly-issued key.
        if any(kw in msg for kw in (
            "SERVICE_KEY_IS_NOT_REGISTERED",
            "SERVICEKEY_IS_NOT_REGISTERED",
            "REGISTERED_SERVICEKEY",
            "SERVICE_KEY_ERROR",
            "DEADLINE_HAS_EXPIRED",
            "UNAUTHORIZED",
            "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS",
        )):
            _LOGGER.warning("Seoul Bus auth check failed: %s", e)
            return "invalid_api_key"
        _LOGGER.warning("Seoul Bus probe couldn't reach API: %s", e)
        return "cannot_connect"
