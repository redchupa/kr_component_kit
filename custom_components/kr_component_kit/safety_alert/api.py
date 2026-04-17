"""Safety Alert API client for Home Assistant integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import curl_cffi
from bs4 import BeautifulSoup

from .exceptions import SafetyAlertConnectionError
from ..const import LOGGER, TZ_ASIA_SEOUL

_BASE_URL = "https://www.safekorea.go.kr/safekorea-kor/ctim/cmsg/calamitySms.do"
_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.safekorea.go.kr/safekorea-kor/ctim/cmsg/calamitySms.do",
    "Origin": "https://www.safekorea.go.kr",
}


class SafetyAlertApiClient:
    """API client for Safety Alert integration."""

    def __init__(self, session=None) -> None:
        pass

    async def async_get_safety_alerts(
        self,
        area_code: str = "1100000000",
        area_code2: Optional[str] = None,
        area_code3: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get safety alerts by scraping calamitySms.do HTML response."""
        end_date = datetime.now(TZ_ASIA_SEOUL)
        start_date = end_date - timedelta(days=7)

        form_data = {
            "bbsSn": "",
            "currentPage": "1",
            "firstYn": "",
            "cOcrcType": "",
            "dsstrSeId": "",
            "sbLawArea1": area_code,
            "sbLawArea2": area_code2 or "",
            "sbLawArea3": area_code3 or "",
            "keyword": "",
            "searchType": "",
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "readYn": "Y",
        }

        try:
            async with curl_cffi.AsyncSession(impersonate="chrome120") as session:
                response = await session.post(
                    _BASE_URL,
                    data=form_data,
                    headers=_HEADERS,
                    verify=False,
                    timeout=15,
                )

                if response.status_code != 200:
                    raise SafetyAlertConnectionError(f"HTTP {response.status_code}")

                html = response.text
                LOGGER.debug("Safety Alert HTML length: %d", len(html))

                return self._parse_html(html)

        except SafetyAlertConnectionError:
            raise
        except Exception as e:
            LOGGER.error("Safety Alert API request failed: %s", e)
            raise SafetyAlertConnectionError(f"Request failed: {e}")

    def _parse_html(self, html: str) -> Dict[str, Any]:
        """Parse disaster SMS data from HTML response."""
        soup = BeautifulSoup(html, "html.parser")
        alerts: List[Dict[str, Any]] = []

        # 웹용 테이블 파싱
        table = soup.select_one("div.board-listarea table tbody")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                # 데이터 없음 행 건너뜀
                if cells[0].get("colspan"):
                    continue

                disaster_type = cells[0].get_text(strip=True)
                msg_cell = cells[1]

                # 메시지, 날짜, 지역 추출 시도
                msg_content = msg_cell.get_text(separator="\n", strip=True)
                lines = [l.strip() for l in msg_content.split("\n") if l.strip()]

                alert = {
                    "DSSTR_SE_NM": disaster_type,
                    "EMRGNCY_STEP_NM": "",
                    "MSG_CN": lines[0] if lines else "",
                    "RCV_AREA_NM": lines[-1] if len(lines) > 1 else "",
                    "REGIST_DT": "",
                }

                # onclick에서 ID 추출 (상세조회용)
                onclick = row.get("onclick", "")
                if "onSubmit" in onclick:
                    import re
                    m = re.search(r"onSubmit\('([^']+)'\)", onclick)
                    if m:
                        alert["SMS_TRSM_SN"] = m.group(1)

                alerts.append(alert)
                LOGGER.debug("Parsed alert: %s", alert)

        if not alerts:
            LOGGER.debug("No alerts found in HTML. Raw snippet: %s", html[2000:3000])

        return {
            "disasterSmsList": alerts,
            "rtnResult": {"totCnt": len(alerts)},
        }
