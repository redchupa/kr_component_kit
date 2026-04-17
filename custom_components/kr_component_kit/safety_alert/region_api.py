"""Safety Alert Region API client for getting region codes."""

from __future__ import annotations

from typing import Dict, List, Optional

from ..const import LOGGER

# 전국 17개 시도 — 행정구역이므로 하드코딩
_SIDO_LIST = [
    {"code": "1100000000", "name": "서울특별시"},
    {"code": "2600000000", "name": "부산광역시"},
    {"code": "2700000000", "name": "대구광역시"},
    {"code": "2800000000", "name": "인천광역시"},
    {"code": "2900000000", "name": "광주광역시"},
    {"code": "3000000000", "name": "대전광역시"},
    {"code": "3100000000", "name": "울산광역시"},
    {"code": "3600000000", "name": "세종특별자치시"},
    {"code": "4100000000", "name": "경기도"},
    {"code": "4200000000", "name": "강원특별자치도"},
    {"code": "4300000000", "name": "충청북도"},
    {"code": "4400000000", "name": "충청남도"},
    {"code": "4500000000", "name": "전북특별자치도"},
    {"code": "4600000000", "name": "전라남도"},
    {"code": "4700000000", "name": "경상북도"},
    {"code": "4800000000", "name": "경상남도"},
    {"code": "5000000000", "name": "제주특별자치도"},
]

# 시군구 하드코딩 데이터 (sido_code → sgg list)
_SGG_DATA: Dict[str, List[Dict[str, str]]] = {
    "4100000000": [  # 경기도
        {"code": "4111000000", "name": "수원시"},
        {"code": "4111100000", "name": "수원시 장안구"},
        {"code": "4111300000", "name": "수원시 권선구"},
        {"code": "4111500000", "name": "수원시 팔달구"},
        {"code": "4111700000", "name": "수원시 영통구"},
        {"code": "4113000000", "name": "성남시"},
        {"code": "4113100000", "name": "성남시 수정구"},
        {"code": "4113300000", "name": "성남시 중원구"},
        {"code": "4113500000", "name": "성남시 분당구"},
        {"code": "4115000000", "name": "의정부시"},
        {"code": "4117000000", "name": "안양시"},
        {"code": "4117100000", "name": "안양시 만안구"},
        {"code": "4117300000", "name": "안양시 동안구"},
        {"code": "4119000000", "name": "부천시"},
        {"code": "4119200000", "name": "부천시 원미구"},
        {"code": "4119400000", "name": "부천시 소사구"},
        {"code": "4119600000", "name": "부천시 오정구"},
        {"code": "4121000000", "name": "광명시"},
        {"code": "4122000000", "name": "평택시"},
        {"code": "4125000000", "name": "동두천시"},
        {"code": "4127000000", "name": "안산시"},
        {"code": "4127100000", "name": "안산시 상록구"},
        {"code": "4127300000", "name": "안산시 단원구"},
        {"code": "4128000000", "name": "고양시"},
        {"code": "4128100000", "name": "고양시 덕양구"},
        {"code": "4128500000", "name": "고양시 일산동구"},
        {"code": "4128700000", "name": "고양시 일산서구"},
        {"code": "4129000000", "name": "과천시"},
        {"code": "4131000000", "name": "구리시"},
        {"code": "4136000000", "name": "남양주시"},
        {"code": "4137000000", "name": "오산시"},
        {"code": "4139000000", "name": "시흥시"},
        {"code": "4141000000", "name": "군포시"},
        {"code": "4143000000", "name": "의왕시"},
        {"code": "4145000000", "name": "하남시"},
        {"code": "4146000000", "name": "용인시"},
        {"code": "4146100000", "name": "용인시 처인구"},
        {"code": "4146300000", "name": "용인시 기흥구"},
        {"code": "4146500000", "name": "용인시 수지구"},
        {"code": "4148000000", "name": "파주시"},
        {"code": "4150000000", "name": "이천시"},
        {"code": "4155000000", "name": "안성시"},
        {"code": "4157000000", "name": "김포시"},
        {"code": "4159000000", "name": "화성시"},
        {"code": "4159100000", "name": "화성시 만세구"},
        {"code": "4159300000", "name": "화성시 효행구"},
        {"code": "4159500000", "name": "화성시 병점구"},
        {"code": "4159700000", "name": "화성시 동탄구"},
        {"code": "4161000000", "name": "광주시"},
        {"code": "4163000000", "name": "양주시"},
        {"code": "4165000000", "name": "포천시"},
        {"code": "4167000000", "name": "여주시"},
        {"code": "4180000000", "name": "연천군"},
        {"code": "4182000000", "name": "가평군"},
        {"code": "4183000000", "name": "양평군"},
    ],
}


class SafetyAlertRegionApiClient:
    """API client for Safety Alert region code retrieval."""

    def __init__(self, session=None) -> None:
        pass

    async def async_get_sido_list(self) -> List[Dict[str, str]]:
        """Return hardcoded list of sido (시도) regions."""
        return _SIDO_LIST

    async def async_get_sgg_list(self, sido_code: str) -> Optional[List[Dict[str, str]]]:
        """Return hardcoded sgg list for the given sido, or None if not available."""
        return _SGG_DATA.get(sido_code)
