"""Korea Bus sub-module constants.

Data source: KakaoMap mobile.  We keep the `KAKAO_*` prefix on the URL/
header constants because they refer to the actual remote endpoints; the
*public-facing* identifiers (domain, classes, entity IDs) use `korea_bus`
so the integration name is decoupled from the underlying backend.
"""
KAKAO_ARRIVALS_URL = "https://m.map.kakao.com/actions/busesInBusStopJson"
KAKAO_SEARCH_URL = "https://m.map.kakao.com/actions/searchView"
KAKAO_STATION_URL = "https://m.map.kakao.com/actions/busStationInfo"
KOREA_BUS_SCAN_INTERVAL = 60

KAKAO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}
