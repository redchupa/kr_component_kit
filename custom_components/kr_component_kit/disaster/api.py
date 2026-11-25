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

async def validate_disaster_api(api_key: str) -> bool:
    try:
        await fetch_disaster_messages(api_key, count=1)
        return True
    except Exception:
        return False


def _parse_payload(text: str) -> list[dict[str, Any]]:
    """Parse XML or JSON safetydata.go.kr response.

    Raises RuntimeError if the body is neither valid XML nor a dict-shaped JSON.
    """
    # Try XML first (production usually returns XML).
    try:
        root = ET.fromstring(text)
        return [
            {
                "message": item.findtext("MSG_CN", ""),
                "area": item.findtext("RCPTN_RGN_NM", ""),
                "create_date": item.findtext("CRT_DT", ""),
                "level": item.findtext("EMRG_STEP_NM", ""),
                "disaster_type": item.findtext("DST_SE_NM", ""),
            }
            for item in root.findall(".//row")
        ]
    except ET.ParseError:
        pass
    # Fall back to JSON.
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        snippet = text[:200].strip()
        raise RuntimeError(
            f"Disaster 응답이 XML/JSON이 아닙니다 (서비스 키 확인): {snippet}"
        ) from e
    if not isinstance(data, dict):
        raise RuntimeError(f"Disaster JSON이 dict가 아닙니다: {type(data).__name__}")
    body = data.get("body", [])
    if not isinstance(body, list):
        raise RuntimeError(f"Disaster JSON 'body' 가 list가 아닙니다: {type(body).__name__}")
    return [
        {
            "message": i.get("MSG_CN", ""),
            "area": i.get("RCPTN_RGN_NM", ""),
            "create_date": i.get("CRT_DT", ""),
            "level": i.get("EMRG_STEP_NM", ""),
            "disaster_type": i.get("DST_SE_NM", ""),
        }
        for i in body
        if isinstance(i, dict)
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
