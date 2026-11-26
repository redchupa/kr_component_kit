"""Disaster message API (재난안전데이터포털)."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any
from ..request_pacing import paced_curl_request

DISASTER_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"
_TIMEOUT = 20

_BROWSER_HEADERS = {
    "Accept": "application/json, text/xml, */*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

_OK_RESULT_CODES = {"00", "0"}


class DisasterApiError(RuntimeError):
    """Raised when safetydata.go.kr returns an explicit error response."""


async def validate_disaster_api(api_key: str) -> bool:
    try:
        await fetch_disaster_messages(api_key, count=1)
        return True
    except Exception:
        return False


def _check_xml_error(root: ET.Element) -> None:
    """Raise DisasterApiError if XML response carries an error header."""
    result_code = (
        root.findtext(".//header/resultCode")
        or root.findtext(".//resultCode")
        or ""
    ).strip()
    result_msg = (
        root.findtext(".//header/resultMsg")
        or root.findtext(".//resultMsg")
        or ""
    ).strip()
    error_msg = (
        root.findtext(".//header/errorMsg")
        or root.findtext(".//errorMsg")
        or ""
    ).strip()
    if (result_code and result_code not in _OK_RESULT_CODES) or error_msg:
        detail = error_msg or result_msg or "알 수 없는 오류"
        raise DisasterApiError(
            f"Disaster API 오류 (code={result_code or '?'}): {detail}"
        )

    # Outer data.go.kr gateway error envelope (cmmMsgHeader / comMsgHeader).
    gateway_code = (
        root.findtext(".//cmmMsgHeader/returnReasonCode")
        or root.findtext(".//comMsgHeader/returnReasonCode")
        or ""
    ).strip()
    gateway_auth = (
        root.findtext(".//cmmMsgHeader/returnAuthMsg")
        or root.findtext(".//comMsgHeader/returnAuthMsg")
        or ""
    ).strip()
    gateway_err = (
        root.findtext(".//cmmMsgHeader/errMsg")
        or root.findtext(".//comMsgHeader/errMsg")
        or ""
    ).strip()
    if (
        (gateway_code and gateway_code not in _OK_RESULT_CODES)
        or gateway_auth
        or gateway_err
    ):
        detail = " / ".join(p for p in (gateway_auth, gateway_err) if p) or "게이트웨이 오류"
        raise DisasterApiError(
            f"Disaster API 게이트웨이 오류 (code={gateway_code or '?'}): {detail}"
        )


def _check_json_error(data: dict[str, Any]) -> None:
    """Raise DisasterApiError if JSON response carries an error header."""
    header = data.get("header")
    if isinstance(header, dict):
        result_code = str(header.get("resultCode") or "").strip()
        result_msg = str(header.get("resultMsg") or "").strip()
        error_msg = str(header.get("errorMsg") or "").strip()
        if (result_code and result_code not in _OK_RESULT_CODES) or error_msg:
            detail = error_msg or result_msg or "알 수 없는 오류"
            raise DisasterApiError(
                f"Disaster API 오류 (code={result_code or '?'}): {detail}"
            )


def _parse_payload(text: str) -> list[dict[str, Any]]:
    """Parse XML or JSON safetydata.go.kr response.

    Raises DisasterApiError if the provider returned an error code/message,
    or RuntimeError if the body is neither valid XML nor a dict-shaped JSON.
    """
    # Try XML first (production usually returns XML).
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        root = None
    if root is not None:
        _check_xml_error(root)
        if root.findtext("./header/resultCode", "").strip() not in _OK_RESULT_CODES:
            raise DisasterApiError("재난문자 응답에 정상 처리 코드가 없습니다.")
        if root.find("./body") is None:
            raise DisasterApiError("재난문자 응답에 본문이 없습니다.")
        return [
            {
                "message": item.findtext("MSG_CN", ""),
                "area": item.findtext("RCPTN_RGN_NM", ""),
                "create_date": item.findtext("CRT_DT", ""),
                "level": item.findtext("EMRG_STEP_NM", ""),
                "disaster_type": item.findtext("DST_SE_NM", ""),
            }
            for item in root.findall("./body//row")
        ]
    # Fall back to JSON.
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise DisasterApiError("재난문자 응답이 XML/JSON 형식이 아닙니다.") from e
    if not isinstance(data, dict):
        raise DisasterApiError(f"Disaster JSON이 dict가 아닙니다: {type(data).__name__}")
    _check_json_error(data)
    header = data.get("header")
    if not isinstance(header, dict) or str(header.get("resultCode")).strip() not in _OK_RESULT_CODES:
        raise DisasterApiError("재난문자 응답에 정상 처리 코드가 없습니다.")
    if "body" not in data:
        raise DisasterApiError("재난문자 응답에 본문이 없습니다.")
    body = data["body"]
    if body is None:
        return []
    if not isinstance(body, list):
        raise DisasterApiError(f"Disaster JSON 'body' 가 list가 아닙니다: {type(body).__name__}")
    if any(not isinstance(item, dict) or "MSG_CN" not in item for item in body):
        raise DisasterApiError("재난문자 응답에 올바르지 않은 항목이 있습니다.")
    return [
        {
            "message": i.get("MSG_CN", ""),
            "area": i.get("RCPTN_RGN_NM", ""),
            "create_date": i.get("CRT_DT", ""),
            "level": i.get("EMRG_STEP_NM", ""),
            "disaster_type": i.get("DST_SE_NM", ""),
        }
        for i in body
    ]


async def fetch_disaster_messages(api_key: str, count: int = 30) -> list[dict[str, Any]]:
    from curl_cffi import requests as cffi_requests

    params = {"serviceKey": api_key, "numOfRows": str(count), "pageNo": "1"}
    async with cffi_requests.AsyncSession(impersonate="chrome120") as session:
        response = await paced_curl_request(session, "GET",
            DISASTER_URL, params=params, headers=_BROWSER_HEADERS, timeout=_TIMEOUT
        )
        if response.status_code != 200:
            raise RuntimeError(f"Disaster API HTTP {response.status_code}")
        return _parse_payload(response.text)
