# 🇰🇷 KR Component Kit

> **한국 거주자를 위한 Home Assistant 통합** — 전기·수도·가스·날씨·재난·약국·학교 급식·실시간 대중교통까지, 한국에서만 쓸 수 있는 15가지 공공 서비스를 한 패키지로.

🇰🇷 **한국어 (이 페이지)** · 🇬🇧 [English README](README.en.md)

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Stargazers][stars-shield]][stars]

[![Open your Home Assistant instance and open a repository inside the HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=redchupa&repository=kr_component_kit&category=integration)

<details>
<summary>🇬🇧 <b>English summary</b></summary>

A Home Assistant custom integration for Korean residents and expats. Exposes 15 Korea-only public services (KEPCO electricity, Seoul water, city gas, KMA weather, disaster alerts, NMC pharmacy, NEIS school meals, Seoul subway + Seoul Bus official API + nationwide bus via KakaoMap, AirKorea air quality, Opinet fuel prices, earthquake warnings) as native HA entities — sensors, weather entities, events, calendars.

All Korean public APIs are free; service keys are obtained from `data.go.kr`, `safetydata.go.kr`, `opinet.co.kr`, `open.neis.go.kr`, and `data.seoul.go.kr` — guides below link directly to each portal's search page.

Optional LLM integration lets you ask in natural Korean ("지금 미세먼지 어때?", "오늘 급식 뭐야?") via HA's Assist conversation agent.

</details>

---

## 🚀 5분 만에 시작하기

### ① 컴포넌트 설치 (2분)

위 **`MY` HACS 뱃지**를 누르면 자동으로 HA가 열립니다 → **DOWNLOAD** → **재시작**.
*HACS가 없으시다면 → [HACS 공식 설치 가이드](https://www.hacs.xyz/docs/setup/download/) 먼저.*

### ② 첫 서비스 등록 (1분) — API 키 ❌ **불필요**

**설정 → 기기 및 서비스 → + 통합 구성요소 추가**
→ 검색창에 `한국 컴포넌트 키트` *(영문 도메인 `kr_component_kit` 도 가능)*
→ **🚨 안전알림** 선택 → 시도/시군구/읍면동 선택 → 제출

### ③ 결과 확인 (30초)

**개발자 도구 → 상태** 에서 친화 이름 `최신 안전알림` 검색 → state에 가장 최근 행안부 안전 메시지 표시.

### ④ 더 많은 서비스 추가

준비되시면 [🔑 API 키 발급 가이드](#-api-키-발급-가이드)대로 다른 12개를 하나씩 추가하시면 됩니다.

---

## 📋 15가지 서비스 한눈에

| 서비스 | 카테고리 | API 키 | 비고 |
|---|---|---|---|
| 💊 **약국** | 생활 | ✅ data.go.kr | 시도/시군구별 약국 + 실시간 영업중 |
| 🚨 **안전알림** | 안전 | ❌ 불필요 | 행안부 안전알림 (스크래핑) |
| 📢 **재난문자** | 안전 | ✅ safetydata.go.kr | 재난문자 실시간 |
| 🌪️ **기상특보** | 안전 | ✅ data.go.kr | 호우/강풍/한파/폭염 12종 |
| 🌍 **지진** | 안전 | ✅ data.go.kr | 반경+규모 필터 |
| ⛅ **기상청 동네예보** | 날씨 | ✅ data.go.kr | HA Weather 카드 호환 |
| 🌫️ **에어코리아** | 날씨 | ✅ data.go.kr (2건) | PM10/PM2.5 + 통합대기질지수 |
| ⚡ **한국전력 (KEPCO)** | 유틸 | ❌ (본인 계정) | 사용량 + 요금 |
| 💧 **아리수 (서울 상수도)** | 유틸 | ❌ (수용가번호) | 서울만 |
| 🏠 **가스앱 (도시가스)** | 유틸 | ❌ (모바일 앱 토큰) | 패킷 캡처 필요 |
| ⛽ **유가 (Opinet)** | 생활 | ✅ opinet.co.kr | 시도별 평균/최저가 |
| 🏫 **학교 (NEIS)** | 생활 | ✅ open.neis.go.kr | 급식·시간표·학사일정 |
| 🚌 **대중교통** | 생활 | 부분 | 지하철: 서울 키 / 버스: 키 불필요 (카카오맵) |
| 🚌 **서울버스 (공식 API)** | 생활 | ✅ data.go.kr | ARS-ID 단위 도착정보 + 옵션에서 정류장 추가/제거 |
| 🚍 **한국 버스 (전국)** | 생활 | ❌ 불필요 | 카카오맵 모바일 — 정류장 **이름 검색** UI, 전국 |

> 💡 **핵심**: 모든 서비스는 **무료** 정부·공공기관 OpenAPI를 사용합니다. 결제·과금 일절 없음.

---

## 🔑 API 키 발급 가이드

> ⚠️ **자주 발생하는 실수 3가지**
> - 재난문자는 `safetydata.go.kr` (안전데이터포털) — `data.go.kr` (공공데이터포털) 과 **다른 포털**. 계정·키 분리.
> - 같은 `data.go.kr` 안에서도 **데이터셋마다 활용신청을 따로** — 약국 신청 키로 기상특보 호출하면 403.
> - 신청 직후 활성화까지 **1~2시간** 걸릴 수 있음 (특히 운영기관 키).

각 서비스의 *바로 검색 링크*는 클릭 한 번에 해당 포털 검색 결과 페이지로 이동합니다 (브라우저가 한국어 자동 인코딩).

### 💊 약국 (전국 약국 정보)

| 항목 | 값 |
|---|---|
| 🌐 포털 | [공공데이터포털 (data.go.kr)](https://www.data.go.kr) |
| 🔎 바로 검색 | [👉 전국 약국 검색 결과로 이동](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=전국%20약국) |
| 검색어 | `전국 약국` 또는 `약국 정보` |
| 운영기관 | 국립중앙의료원 (코드 `B552657`) |
| 정확한 데이터셋명 | **국립중앙의료원_전국 약국 정보 조회 서비스** |
| 코드 호출 endpoint | `apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire` |

**신청 단계:** 회원가입 → 위 검색 링크 클릭 → 데이터셋 선택 → **활용신청** → 마이페이지 → 오픈API → 인증키 발급현황 → **일반 인증키(Decoding)** 복사 → HA 약국 항목에 그대로 붙여넣기.

---

### 📢 재난문자 *(✅ 작동 검증 완료 — 2026-05-14)*

| 항목 | 값 |
|---|---|
| 🌐 포털 | [행정안전부 안전데이터공유플랫폼 (safetydata.go.kr)](https://www.safetydata.go.kr) |
| 운영기관 | 행정안전부 |
| 정확한 데이터셋명 | **행정안전부_긴급재난문자** |
| 코드 호출 endpoint | `/V2/api/DSSP-IF-00247` |
| 발급 방식 | 운영자 검토 후 발급 *(즉시 자동 발급 ❌, 1~3 영업일)* |
| 일일 호출 한도 | 기본 1,000건. 통합은 5분 폴링이라 288건/일 사용 → 충분 |
| 키 유효기간 | **1년** *(만료 후 마이페이지에서 재발급 — 만료일자 화면에서 확인)* |
| 키 형태 | **단일 형태만 제공** *(data.go.kr 처럼 Decoding/Encoding 두 가지 ❌)* |
| IP 필수 | ⚠️ **신청서에 호출할 IP 등록 필수** (아래 3️⃣ 참고) |

> ⚠️ 안전데이터공유플랫폼은 공공데이터포털과 **다른 사이트**입니다. 이미 `data.go.kr` 계정이 있어도 별도 가입이 필요합니다.

#### 1️⃣ 회원가입
[safetydata.go.kr](https://www.safetydata.go.kr) 회원가입. `data.go.kr` 계정으로는 로그인되지 않습니다.

#### 2️⃣ 데이터셋 선택 *(⚠️ 두 카드 헷갈리기 쉬움)*
상단 검색창에 `재난문자` → 검색 결과 카드를 보면 **두 개**가 나옵니다:

| 카드 | 사용 여부 |
|---|---|
| **행정안전부_긴급재난문자** *(조회 5만+ / 다운로드 28M / `#재난문자` 태그)* | ✅ **이걸 신청** |
| 재난문자(속보) *(조회 900+ / 태그 `#-1`)* | ❌ endpoint 코드가 달라 통합과 호환 안 됨 |

올바른 카드 클릭 → 상세 페이지에서 endpoint 가 `DSSP-IF-00247` 인지 한 번 확인.

#### 3️⃣ 활용신청 폼 작성

상세 페이지 → **오픈API 활용신청** 버튼 → 폼 작성:

**① 활용목적** *(필수)*
- 카테고리: **`앱개발 (모바일, 솔루션 등)`** 권장
- 설명 예시: *"홈어시스턴트(Home Assistant) 컴포넌트로 가족·본인에게 긴급재난문자 알림을 받게 할 목적"*

**② 하루 최대 호출 횟수** *(필수)*
- **`1000`** 입력. 통합이 5분 주기로 288회/일만 사용하므로 충분합니다.

**③ 아이피** *(필수)* — 가장 중요한 부분
호출이 들어올 **HA 서버의 공인(외부) IP** 를 등록해야 합니다. 등록 IP와 실제 호출 IP가 다르면 키가 발급돼도 **403 거부**.

| 옵션 | 입력 예시 | 추천도 |
|---|---|---|
| 개인 IP | `121.123.45.67` | 가장 엄격. 하지만 **한국 가정용 인터넷은 dynamic IP** 라 며칠~몇 달 안에 바뀜 → 재신청 필요 |
| 대역 허용 | `121.123.*.*` | ISP가 비슷한 대역 안에서 갱신해주는 경우 안전. 일반적으로 무난 |
| 전체 허용 | `*.*.*.*` | ⭐ **개인 사용자 추천** — IP 변경 신경 안 써도 됨. 키 자체가 비밀이라 보안 영향 미미 |

🔎 **HA 서버의 공인 IP 확인 방법:**
부가기능 → **Terminal & SSH** (또는 SSH로 접속) → 다음 명령 실행:
```bash
curl -s https://api.ipify.org
```
출력된 IP가 신청서에 넣을 값.

**④ 라이선스 동의** → **이용신청** 버튼 클릭.

#### 4️⃣ 승인 대기
마이페이지 → "데이터 활용신청 내역" 에서 상태 확인:
- *"승인 대기 중입니다"* → 운영자 검토 중. **자동 발급이 아니므로 영업일 기준 1~3일 정도 대기** 예상.
- *"발급됨"* → 서비스키 값이 노출되고 키 사용 가능.

#### 5️⃣ 키 복사 → HA 입력
마이페이지 → 발급된 키 옆 **"값 복사하기"** 클릭 → HA 통합 추가 시 **재난문자** 선택 → 인증키 필드에 그대로 붙여넣기.

> 💡 safetydata.go.kr 은 키를 **한 가지 형태로만** 제공합니다 (data.go.kr 의 Decoding/Encoding 구분 없음). "값 복사하기" 로 받은 문자열을 그대로 붙여넣으면 됩니다. 통합 코드가 내부적으로 URL 인코딩을 자동 처리합니다.

#### 🔁 사후 관리

- **호출량 모니터링**: 마이페이지 화면의 `일일호출량 / 호출량` 표시 — 앞 숫자가 한도(1000), 뒤 숫자가 **현재까지 누적 사용 횟수** (0이면 "최대" 가 아니라 "아직 안 씀"). 한도 초과 시 다음 날 0시 리셋.
- **IP 변경 신청**: 가정용 dynamic IP 가 바뀐 경우 마이페이지 → 해당 키 → **목록 변경신청** → IP 필드 수정. ⚠️ 변경 역시 운영자 검토 거침. 자주 바뀐다면 처음부터 `*.*.*.*` 로 변경 신청 권장.
- **키 만료 (1년)**: 만료일자 도래 전에 마이페이지 → 변경신청으로 갱신 가능. 만료되면 401 발생.

#### 🆘 작동 안 될 때

| 증상 | 원인 후보 | 해결 |
|---|---|---|
| `401 / SERVICE KEY ERROR` | 키 활성화 전 / 만료 / 복사 시 공백 포함 | 발급 직후라면 30분~1시간 대기 후 재시도. 만료일자 확인. 키 앞뒤 공백·따옴표 제거 후 재입력 |
| `403 / ACCESS_DENIED` | **IP 불일치 (가장 흔함)** | `curl -s https://api.ipify.org` 결과와 마이페이지 등록 IP 비교. 불일치면 **목록 변경신청** 으로 IP 수정. 자주 바뀐다면 `*.*.*.*` 로 갱신 |
| 응답이 비었음 / `body []` | 정상 — 최근 재난문자가 없는 시간대 | 조용한 시간에는 빈 응답이 정상. 큰 재난·기상특보 시 채워짐 |

---

### 🌪️ 기상특보 + 🌍 지진 + ⛅ 동네예보 (기상청 3종 — 같은 인증키)

세 데이터셋 모두 `data.go.kr` 운영기관 **기상청** (`1360000`). 인증키는 *내 계정의 하나의 키*를 그대로 사용하지만, **활용신청은 각각 따로** 해야 합니다.

| 서비스 | 바로 검색 | 검색어 | endpoint |
|---|---|---|---|
| 🌪️ 기상특보 | [👉 기상특보 검색](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=기상특보) | `기상특보` | `1360000/WthrWrnInfoService` |
| 🌍 지진정보 | [👉 지진정보 검색](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=지진정보) | `지진정보` | `1360000/EqkInfoService` |
| ⛅ 단기예보 | [👉 단기예보 검색](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=단기예보) | `단기예보` | `1360000/VilageFcstInfoService_2.0` |

---

### 🌫️ 에어코리아 (대기질) — **2건 필수**

`data.go.kr` 운영기관 **한국환경공단** (`B552584`) 의 데이터셋 2건을 각각 활용신청해야 합니다.

| 데이터셋 | 바로 검색 | 검색어 | endpoint |
|---|---|---|---|
| 측정소정보 | [👉 측정소정보](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=에어코리아%20측정소) | `에어코리아 측정소` | `B552584/MsrstnInfoInqireSvc` |
| 대기오염정보 | [👉 대기오염정보](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=에어코리아%20대기오염) | `에어코리아 대기오염` | `B552584/ArpltnInforInqireSvc` |

> 💡 측정소정보 빠지면 HA 설정 화면의 측정소 dropdown이 비어 보입니다.

> ⚠️ **옵션 — 생활기상지수 (UV·대기정체)**: 사용하려면 추가로 `생활기상지수` 검색 → 기상청 데이터셋 활용신청. 단 코드는 V4 endpoint 호출이지만 포털은 V5로 업그레이드된 상태로 보입니다 — 실제 동작 미검증. 등록 후 HA 로그(`LivingWthrIdx` 검색)로 확인하세요. 미작동 시 issue 부탁드립니다.

---

### ⛽ 유가 (Opinet)

| 항목 | 값 |
|---|---|
| 🌐 포털 | [👉 Opinet 오피넷 API 신청 페이지](https://www.opinet.co.kr/user/api/empApiInfo.do) |
| 발급 절차 | 무료 회원가입 → API 신청 → 즉시 발급 |
| 코드 호출 endpoint | `opinet.co.kr/api/avgAllPrice.do`, `lowTop10.do` |

> 💡 Opinet은 공공데이터포털과 **별개 포털**입니다.

---

### 🏫 학교 (NEIS)

| 항목 | 값 |
|---|---|
| 🌐 포털 | [👉 NEIS 교육정보 개방 포털](https://open.neis.go.kr) |
| 발급 절차 | 회원가입 → 인증키 신청 → 마이페이지 "신청현황" 에서 확인 |
| 코드 호출 endpoint | `open.neis.go.kr/hub/...` |

> 💡 NEIS도 공공데이터포털과 **별개 포털**입니다. 학교명은 HA 설정에서 자동 검색됩니다 (학교명만 입력하면 dropdown 표시).

---

### 🚌 대중교통 / 서울버스 / 한국 버스 — 무엇을 고를까?

버스/지하철 관련해 메뉴에 **세 가지 항목**이 보입니다. 시나리오별 정리:

| 메뉴 | 데이터 소스 | API 키 | 특징 | 추천 사용자 |
|---|---|---|---|---|
| 🚌 **대중교통 (지하철 / 버스)** | 서울 열린데이터광장 (지하철) + 카카오맵 (버스) | 지하철은 ✅, 버스는 ❌ | 한 통합에 지하철역 + 버스정류장 혼합 등록. 환승경로 옵션 키도 지원 | 지하철·버스 모두 쓰는 서울/수도권 사용자 |
| 🚌 **서울버스 (공식 API)** | 서울특별시 정류소정보조회 API (ws.bus.go.kr) | ✅ data.go.kr | 공식 API 기반 가장 정확. ARS-ID 입력 → 자동으로 노선 목록 조회. 정류장당 새로고침 버튼 + 옵션에서 정류장 추가/제거/노선 편집 | 서울만 다니고 공식 API 안정성을 원하는 사용자 |
| 🚍 **한국 버스 (전국)** | 카카오맵 모바일 | ❌ 불필요 | 정류장 **이름 검색** UI. 전국 대부분 정류장. 옵션에서 폴링 주기 변경 (30s~1h) | 키 발급이 부담스럽거나, 서울 외 지역 사용자 |

**서울버스 / 한국 버스 — 무엇이 다른가?**

- 같은 정류장이라도 데이터 소스가 다르면 응답이 약간 다를 수 있습니다 (예: "곧 도착" vs "1분 후"). 서울버스는 공식 API라 가장 정확, 한국 버스는 카카오맵 모바일 사이트라 사이트 개편 시 일시 깨질 위험.
- 두 통합을 **동시에** 등록해도 무방 (서로 독립). 비교용으로 쓰시는 분도 있습니다.

**카카오맵 정류장 ID 찾는 법** *("대중교통" 메뉴의 버스 등록 시. "한국 버스"는 이름 검색이라 ID 불필요)*:
[카카오맵](https://map.kakao.com) → 정류장 검색 → 정류장 클릭 → URL `?busstopid=03171&...` → **`busstopid=` 뒤의 값** 복사 (예: `03171`, `BS09013700`).

**서울버스 ARS-ID 찾는 법** *("서울버스" 메뉴 등록 시)*:
[bus.go.kr](https://bus.go.kr) 또는 정류장 표지판에 적힌 5자리 정류소번호 (예: `23288` = 사당역).

---

## ⚙️ 등록·재설정 흐름

### 새 항목 등록
설정 → 기기 및 서비스 → **+ 통합 구성요소 추가** → `한국 컴포넌트 키트` 검색 → 원하는 서비스 선택.

> 한 통합에 13개 서비스가 메뉴로 들어있어, 추가하려는 서비스마다 한 번씩 등록합니다. **같은 서비스를 여러 지역으로 중복 등록**도 가능 (예: 약국을 시흥시·안양시·부모님 댁 시군구 3번 등록).

### 등록 후 변경 (API 키 갱신 / 지역 추가 등)
해당 항목 옆 **"구성"** 버튼 → 입력값 편집. *(삭제·재등록 없이 가능. entity와 자동화 연결 유지됨.)*

### 입력값 어디서 받는가?

| 서비스 | 어디서 받는가 |
|---|---|
| ⚡ **KEPCO** | 한전 홈페이지 ID/비밀번호 (본인 계정, 2차 인증 미지원) |
| 💧 **아리수** | 종이 고지서 또는 [아리수 사이버 고객센터](https://i-arisu.seoul.go.kr) → 요금조회 좌측 수용가번호 + 고객명 |
| 🏠 **가스앱** | 사용계약번호는 가스앱 모바일 앱 → 내 정보. 토큰·회원ID는 mitmproxy 등으로 모바일 앱 HTTPS 요청의 `X-Token`/`X-Member` 헤더 추출 (⚠️ 고급 사용자용) |
| 🌍 **지진 좌표** | 기본값은 서울시청 (`37.5665, 126.978`). **본인 집 좌표로 꼭 변경.** 기본 반경 200km / 최소 규모 3.0 |

---

## 🎁 등록하면 만들어지는 entity

> entity_id는 한국어 → 로마자 슬러그 자동 변환 (예: `약국 - 시흥시` + `운영 약국 수` → `sensor.yaggug_siheungsi_unyeong_yaggug_su`). 정확한 ID는 **개발자 도구 → 상태** 에서 친화 이름으로 검색해 확인.

| 서비스 | 친화 이름 (sensor 등) | 주요 attribute |
|---|---|---|
| 💊 약국 | `운영 약국 수` | `pharmacies[]` (최대 50: name·address·phone·lat·lon·today_hours·`open_now`·duty_time), `total`, `shown`, `open_now_count` |
| 🚨 안전알림 | `최신 안전알림`, `안전알림 수`, `오늘 안전알림 여부` (binary), `안전알림 이벤트` (event) | `latest`, `alerts[]`, `count` |
| 📢 재난문자 | `최신 재난문자`, `재난문자 수`, `재난문자 이벤트` (event) | `level`, `area`, `disaster_type` |
| 🌪️ 기상특보 | `호우 특보`/`강풍 특보`/`한파 특보`/... (event 12종) | state: `advisory`/`warning`/`pre_*`/`cancelled`/`none`, `start_time`, `end_time` |
| 🌍 지진 | `지진 경보` (event) | `magnitude`, `location`, `distance_km`, `datetime` |
| ⛅ 동네예보 | (weather 엔티티 1개 — HA 기본 Weather 카드 호환) | hourly/daily forecast 서비스 지원 |
| 🌫️ 에어코리아 | `PM10 미세먼지`, `PM2.5 초미세먼지`, `O₃ 오존`, `NO₂ 이산화질소`, `SO₂ 아황산가스`, `CO 일산화탄소`, `통합대기질지수` + binary `대기질 경보` + event + calendar `대기질 예보` | 등급(Grade) 동반 |
| ⚡ KEPCO | `현재 사용량` (kWh), `지난달 요금` (원), `예상 요금` (원), `고객번호`, `전력구분` | — |
| 💧 아리수 | `수도 요금` (원), `사용량` (㎥), `청구월` | `billing_month`, `customer_info`, `arrears_info` |
| 🏠 가스앱 | `청구 제목`, `총 요금` (원) | — |
| ⛽ 유가 | `전국 평균가`, `최저가` (등록한 시도×유종 조합마다) | `ranking[]` (Top 5 주유소 이름·가격·주소) |
| 🏫 학교 | `급식`, `학교 정보` + calendar 학사일정/시간표 | 급식: `menu`, `calorie`, `allergy_codes` |
| 🚌 대중교통 | `<역/정류장> ... 도착` (TIMESTAMP — HA가 "N분 후"로 자동 표시) | — |
| 🚌 서울버스 | 노선당 도착 sensor 2개 (`<rtNm> 다음`, `<rtNm> 다다음`, TIMESTAMP) + 정류장당 새로고침 버튼 1개 | `vehicle_number`, `current_stop`, `message`, `remain_seat`, `direction`, `bus_type`, `status` ("곧 도착", "N분 후") |
| 🚍 한국 버스 | 노선당 도착 sensor 2개 (`<번호> 다음`, `<번호> 다다음`, TIMESTAMP) + 정류장당 새로고침 버튼 1개 | `vehicle_number`, `current_stop`, `message`, `remain_seat`, `next_stop`, `first_time`/`last_time`/`intervals`, `bus_type`, `status` |

---

## 🎨 대시보드 예제 — 약국 가까운 순 + 영업중 필터 + 카카오맵 길찾기

검색·필터 헬퍼 두 개 먼저:
- **설정 → 헬퍼 → 텍스트**: `input_text.yaggug_geomsaeg` ("약국 검색")
- **설정 → 헬퍼 → 토글**: `input_boolean.yaggug_yeongeobjungman` ("약국 영업중만")

대시보드 YAML *(섹션/vertical-stack에 통째로 붙여넣기. 본인 약국 entity_id로 변경)*:

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: 💊 운영 약국
    heading_style: title
    icon: mdi:pharmacy

  - type: horizontal-stack
    cards:
      - type: tile
        entity: sensor.yaggug_siheungsi_unyeong_yaggug_su  # 본인 entity_id
        name: 전체 약국
        icon: mdi:pharmacy-marker
        color: green
      - type: tile
        entity: sensor.yaggug_siheungsi_unyeong_yaggug_su
        name: 지금 영업 중
        icon: mdi:clock-check
        color: blue
        state_content: open_now_count

  - type: entities
    title: 검색 / 필터
    show_header_toggle: false
    entities:
      - entity: input_text.yaggug_geomsaeg
        name: 🔍 이름 검색
      - entity: input_boolean.yaggug_yeongeobjungman
        name: 🟢 지금 영업 중만

  - type: markdown
    title: 약국 목록 (가까운 순)
    content: |
      {% set tracker = 'zone.home' %}
      {% set sensor_id = 'sensor.yaggug_siheungsi_unyeong_yaggug_su' %}
      {% set my_lat = state_attr(tracker, 'latitude') | float(0) %}
      {% set my_lon = state_attr(tracker, 'longitude') | float(0) %}
      {% set ph = state_attr(sensor_id, 'pharmacies') or [] %}
      {% set raw_query = states('input_text.yaggug_geomsaeg') | default('', true) %}
      {% set query = '' if raw_query in ['unknown', 'unavailable', 'none', None] else raw_query | lower | trim %}
      {% set open_only = is_state('input_boolean.yaggug_yeongeobjungman', 'on') %}
      {% set step1 = ph if not query else ph | selectattr('name', 'search', query) | list %}
      {% set filtered = step1 | selectattr('open_now') | list if open_only else step1 %}
      {% set ns = namespace(items=[]) %}
      {% for p in filtered %}
        {% set d = distance(my_lat, my_lon, p.lat | float(0), p.lon | float(0)) %}
        {% set ns.items = ns.items + [(d, p)] %}
      {% endfor %}
      {% set ranked = ns.items | sort %}
      **표시 {{ ranked | length }}곳** · 기준 `{{ tracker }}`
      {% if query %}· 검색 `{{ query }}`{% endif %}{% if open_only %}· 영업중만{% endif %}

      ---
      {% for d, p in ranked[:15] %}
      {% set dist_label = ((d * 1000) | round(0) | int | string) + 'm' if d < 1 else ((d | round(1) | string) + 'km') %}
      ### {{ '🟢' if p.open_now else '⚪' }} {{ p.name }} · _{{ dist_label }}_
      - 📍 {{ p.address }}
      - 📞 [{{ p.phone or '번호 없음' }}](tel:{{ (p.phone or '') | replace('-','') }})
      - 🕐 {{ ('지금 영업 중 (' + p.today_hours + ')') if p.open_now else (('오늘 ' + p.today_hours) if p.today_hours else '오늘 휴무') }}
      - 🗺️ [카카오맵](https://map.kakao.com/link/map/{{ p.name | urlencode }},{{ p.lat }},{{ p.lon }}) · [길찾기](https://map.kakao.com/link/to/{{ p.name | urlencode }},{{ p.lat }},{{ p.lon }})

      {% endfor %}
```

> 💡 위치 기준을 폰 따라가게 하려면 `tracker = 'zone.home'`을 `person.<본인>` 또는 `device_tracker.<폰>` 으로 변경.

---

## 🤖 자연어로 묻기 (LLM 옵션)

HA의 **Assist + LLM 통합** (OpenAI / Google / Ollama 등)에 본 컴포넌트를 노출하면 한국어로 직접 물을 수 있습니다.

| 질문 | 매칭 서비스 |
|---|---|
| "지금 영업중인 가까운 약국 알려줘" | 💊 약국 |
| "오늘 미세먼지 어때?" | 🌫️ 에어코리아 |
| "내일 비 와?" | ⛅ 기상청 |
| "최근 재난문자 뭐 있어?" | 📢 재난문자 |
| "오늘 급식 뭐야?" | 🏫 학교 |
| "다음 버스 언제 와?" | 🚌 대중교통 |

LLM에 노출 안 해도 일반 sensor/event/weather 엔티티로 정상 동작. 추가 설정 불필요.

---

## ❓ FAQ

<details>
<summary><b>13가지를 전부 등록해야 하나요?</b></summary>

아니요. 원하는 것만 등록하시면 됩니다. 등록 안 한 서비스는 entity·리소스를 전혀 쓰지 않습니다.
</details>

<details>
<summary><b>사용료가 드나요?</b></summary>

**전부 무료**. 정부·공공기관 OpenAPI를 사용하며 본 컴포넌트도 결제·과금 없음. 각 API는 일일 호출 한도(보통 1만~100만회/일)가 있지만 가정용 1인 사용으로 넘기는 일은 거의 없습니다.
</details>

<details>
<summary><b>API 키 신청이 부담스러워요</b></summary>

**키 없이 바로 되는 서비스 4가지**부터 체험하세요:
- 🚨 **안전알림** — 지역만 선택 (행안부 페이지 스크래핑)
- ⚡ **한국전력 / 💧 아리수 / 🏠 가스앱** — 본인 계정/번호로 로그인 (API 키 아님)
</details>

<details>
<summary><b>서울 외 거주자도 가능한가요?</b></summary>

대부분 전국 가능. **서울 전용**: 아리수(상수도), 서울 지하철 실시간 도착정보. 나머지는 전국 OK.
</details>

<details>
<summary><b>등록한 API 키·지역을 바꾸려면?</b></summary>

설정 → 기기 및 서비스 → **"한국 컴포넌트 키트"** 카드 → 해당 항목의 **"구성"** 버튼. 삭제·재등록 없이 entity와 자동화 연결 유지됨.
</details>

<details>
<summary><b>같은 서비스를 여러 지역으로 등록 가능?</b></summary>

가능합니다. 약국 서비스를 시흥시·안양시·부모님 댁 3번 등록하면 독립적인 기기·entity 3세트가 만들어집니다.
</details>

<details>
<summary><b>핸드폰 알림과 함께 쓰려면?</b></summary>

HA Automation + Companion 앱 푸시 조합. 가장 단순한 예시:

```yaml
automation:
  - alias: "재난문자 → 핸드폰 푸시"
    trigger:
      - platform: state
        entity_id: sensor.<재난문자_최신_엔티티_id>   # 개발자 도구에서 확인
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state not in ['없음', 'unknown', 'unavailable'] }}"
    action:
      - service: notify.mobile_app_<폰_이름>
        data:
          title: "🚨 재난문자"
          message: "{{ trigger.to_state.state }}"
```
</details>

<details>
<summary><b>입력한 비밀번호·키는 어디 저장되나요?</b></summary>

Home Assistant 내부 저장소 (`.storage/`) 에만 저장되며 외부로 전송되지 않습니다. 입력한 비밀번호는 API 호출 시 해당 서비스(한전·아리수 등)의 공식 페이지에만 사용됩니다.
</details>

<details>
<summary><b>업데이트는 어떻게 받나요?</b></summary>

HACS로 설치하셨다면 새 릴리즈 시 **HACS → 통합 → KR Component Kit** 에 빨간 점 표시 → UPDATE → HA 재시작. 기존 설정·entity 유지됨.
</details>

<details>
<summary><b>신축 아파트인데 시군구 목록에 내 동이 없어요</b></summary>

행정구역 코드가 신축 동까지 즉시 반영되지 않는 경우가 있습니다. 가장 가까운 인접 동/구를 선택해 주세요. 기상청 동네예보는 5km×5km 격자라 인접 코드 선택해도 실제 날씨 거의 동일.
</details>

---

## 🔄 업데이트 주기

| 카테고리 | 서비스 | 주기 |
|---|---|---|
| 실시간 | 버스/지하철 (대중교통 메뉴) | 1~2분 |
| 실시간 | 서울버스 / 한국 버스 | 1분 (서울버스 고정) / 30s~1h 조정 가능 (한국 버스) |
| 안전·재난 | 재난문자, 안전알림, KEPCO | 5분 |
| 안전·재난 | 지진, 기상특보 | 10~15분 |
| 환경/유틸 | 가스앱, 기상청 예보, 에어코리아 | 20~30분 |
| 생활 | 아리수, 약국, 유가 | 1시간 |
| 생활 | 학교 (급식·시간표) | 6시간 |

> 💡 약국 `open_now`(지금 영업중) 는 데이터 갱신과 별개로 **대시보드 렌더 시마다 실시간 재계산**.

---

## ⚠️ 알려진 한계 (정직한 공개)

본 컴포넌트는 일부 서비스에서 비공식 경로(스크래핑·모바일 앱 API)를 사용합니다. 외부 사이트 변경 시 일시적으로 깨질 수 있는 약점을 모두 공개합니다.

| 서비스 | 한계 |
|---|---|
| 🚨 **안전알림 / 📢 재난문자** | `safekorea.go.kr` HTML 스크래핑 / `safetydata.go.kr` API. 정부 사이트 점검 시 일시 미작동 가능. 재난문자는 chrome 5종 impersonation rotation 지원, 안전알림은 chrome120 단일 |
| ⚡ **KEPCO** | 한전 페이지명 변경 시 로그인 감지 실패 가능 (2FA 미지원). HA 로그 `KEPCO login: unknown redirect` 로 디버깅 |
| 💧 **아리수** | 서울시청 페이지(`i121.seoul.go.kr`) HTML 구조 변경 시 파싱 실패 가능. 9자리 수용가번호 가정 |
| 🏠 **가스앱** | 모바일 앱 내부 API. 패킷 캡처(mitmproxy/Charles)로 토큰 추출 필요 — 일반 사용자에게 부담 큼 |
| 🌫️ **에어코리아 생활지수 (UV·대기정체)** | 코드는 V4 endpoint 호출, 포털은 V5로 업그레이드된 듯 — 실제 동작 미검증. 미세먼지(필수 2건)는 영향 없음 |
| 🏫 **NEIS** | 데이터 없는 날(방학·휴일)에 `INFO-200` 응답을 에러로 처리 → 일시 에러 로그 가능 (실제 동작에는 영향 적음) |

> ✅ **검증 완료**: 약국 (시흥시 — 실제 sensor state=20, 20개 약국 attribute 정상). 안전알림 (시흥시 은행동 cascading 등록 성공). 재난문자 (safetydata.go.kr 키 발급 → entity 정상 동작, 2026-05-14).

> 🐛 **사이트 변경으로 깨졌다면** [GitHub Issues](https://github.com/redchupa/kr_component_kit/issues)에 알려주세요. 빠르게 수정 PR 작성합니다.

---

## 🐛 문제 해결

### API 키 인증 실패
- 신청 후 활성화까지 **1~2시간** 대기 (특히 운영기관 키)
- `data.go.kr` 안에서도 **데이터셋별 활용신청 별도** — 약국 키로 기상특보 호출하면 403
- 재난문자는 `safetydata.go.kr` 별도 포털 — `data.go.kr` 키로는 안 됨
- `401` = 키 자체가 잘못, `403` = 키는 맞지만 해당 데이터셋 활용신청 안 됨
- 일일 트래픽 한도 초과도 동일 증상 (마이페이지에서 확인)

### 로그인 실패 (KEPCO / 아리수 / 가스앱)
- 웹사이트에서 직접 로그인 가능한지 확인
- 2차 인증(OTP) 설정된 계정은 미지원
- 가스앱은 토큰이 자주 만료 — 앱에서 다시 발급

### 데이터가 비어있을 때 (안전알림 / 재난문자)
- 등록한 지역에 최근 메시지가 없으면 sensor state가 `없음` — 정상 동작
- 정부 사이트 점검 중이면 잠시 후 자동 복구

### 그래도 안 풀리면

1. **로그 확인** — 설정 → 시스템 → 로그 에서 `kr_component_kit` 검색
2. **이슈 등록** — [GitHub Issues](https://github.com/redchupa/kr_component_kit/issues) — 다음 정보 포함:
   - 어떤 서비스 (예: "약국 — 서울 강남구")
   - HA 버전 + 본 컴포넌트 버전
   - 로그 에러 (개인정보·키는 가린 후)
   - 시도한 단계

> 💬 한국어 그대로 작성해주셔도 됩니다. 답변도 한국어로.

---

## 📋 요구사항

- **Home Assistant** 2023.1.0 이상
- **Python** 3.11 이상 (HA 자체 요구사항)
- **인터넷 연결** (각 서비스 API 접근)
- 자동 설치 패키지: `curl_cffi>=0.7.0`, `beautifulsoup4>=4.12.0` (manifest.json 정의)

---

## ⚠️ 면책조항

- 본 컴포넌트는 일부 서비스에서 공식 API가 아닌 **인증된 웹 스크래핑 / 모바일 앱 내부 API** 를 사용합니다 (KEPCO, 아리수, 가스앱, 안전알림)
- 각 서비스 제공업체의 정책 변경에 따라 동작하지 않을 수 있습니다
- 정부 사이트 일부는 TLS 검증 우회 (`verify=False`) — 정부 사이트의 TLS 설정 호환성 이슈 회피용. 보안에 민감하시면 코드를 직접 확인해 주세요
- 개인정보(ID/비밀번호/토큰/API 키)는 Home Assistant 내부 저장소에만 보관되며 외부 전송 없음
- 본 프로젝트는 정부·공공기관과 무관한 **비공식 서드파티 통합**. 사용자의 책임 하에 이용해 주세요.

---

## 🤝 기여 / 라이선스

- 라이선스: [MIT](LICENSE) — 자유롭게 사용·수정·재배포 가능
- 이슈·PR 환영: <https://github.com/redchupa/kr_component_kit/issues>
- 새 한국 서비스 추가 제안도 환영합니다

---

## ⭐ 도움이 되셨다면

오른쪽 상단 **Star ⭐** 한 번이면 큰 도움이 됩니다. 별이 모이면 HACS Default Repository 등록 가능성이 올라가고, 더 많은 한국 사용자가 발견할 수 있습니다.

[![Star History Chart](https://api.star-history.com/svg?repos=redchupa/kr_component_kit&type=Date)](https://star-history.com/#redchupa/kr_component_kit&Date)

---

## ☕ 후원

이 프로젝트가 도움이 되셨다면 커피 한 잔으로 응원해 주세요 🙏

<table>
  <tr>
    <td align="center">
      <b>토스</b><br/>
      <img src="https://raw.githubusercontent.com/redchupa/kr_component_kit/main/images/toss-donation.png" alt="Toss 후원 QR" width="200"/>
    </td>
    <td align="center">
      <b>PayPal</b><br/>
      <img src="https://raw.githubusercontent.com/redchupa/kr_component_kit/main/images/paypal-donation.png" alt="PayPal 후원 QR" width="200"/>
    </td>
  </tr>
</table>

---

**Made with ❤️ for Korean Home Assistant Users**

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/redchupa/kr_component_kit.svg?style=for-the-badge
[releases]: https://github.com/redchupa/kr_component_kit/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/redchupa/kr_component_kit.svg?style=for-the-badge
[commits]: https://github.com/redchupa/kr_component_kit/commits/main
[license-shield]: https://img.shields.io/github/license/redchupa/kr_component_kit.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/redchupa/kr_component_kit.svg?style=for-the-badge
[stars]: https://github.com/redchupa/kr_component_kit/stargazers
