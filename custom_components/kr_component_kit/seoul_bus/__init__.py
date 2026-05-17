"""Seoul Bus sub-module constants."""
# 서울특별시_정류소정보조회 서비스의 상세기능 #7 (`getStationByUidItem`)을
# 호출한다.  공식 활용가이드 기준 "상세기능명"은 `getStationByUidItem` 인데
# 실제 Call Back URL 의 경로는 `getStationByUid` 라 두 이름이 다르다.
# 헷갈리기 쉬워서 명시.
SEOUL_BUS_STATION_URL = (
    "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
    "?ServiceKey={key}&arsId={ars_id}"
)
SEOUL_BUS_SCAN_INTERVAL = 60
