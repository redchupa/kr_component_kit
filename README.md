# 🇰🇷 KR Component Kit

> 대한민국에서만 사용할 수 있는 Home Assistant 통합 구성요소
> Home Assistant integration for Korea-only services — utilities, weather/disaster alerts, transit, school meals, and more.

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Stargazers][stars-shield]][stars]

[![Open your Home Assistant instance and open a repository inside the HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=redchupa&repository=kr_component_kit&category=integration)

한국전력, 아리수, 가스앱부터 기상청 동네예보·재난문자·지진·약국·학교 급식·실시간 대중교통까지 — 대한민국에서만 쓸 수 있는 13가지 서비스를 Home Assistant 한 곳에서 모니터링할 수 있게 해주는 통합 구성요소입니다.

---

## 👋 처음이세요? 이렇게 따라오세요

**이 컴포넌트로 할 수 있는 일을 한마디로** — 한국 공공 서비스(전기·수도·가스·날씨·재난·약국·학교 급식 등)의 데이터를 Home Assistant의 **센서(sensor)·이벤트(event)·날씨(weather) 엔티티**로 만들어 줍니다. 만들어진 엔티티는 대시보드에 표시하거나, 자동화의 트리거로 쓰거나, 음성비서(Assist)로 물어볼 수 있습니다.

### 🧭 추천 읽기 순서

| 상황 | 추천 섹션 |
|---|---|
| Home Assistant 자체가 처음이라면 | [공식 한국어 시작 가이드](https://www.home-assistant.io/installation/) 먼저 본 뒤 돌아오세요 |
| HACS가 뭔지 모르겠다면 | [HACS란?](#-hacs가-처음이라면) → [설치 방법](#-설치-방법) |
| **API 키부터 받아야 하는지 모르겠다면** | [🚀 5분 만에 시작하기](#-5분-만에-시작하기-api-키-필요-없음) (API 키 없이 시작) |
| 약국·재난문자·기상청 등 키가 필요한 서비스 | [🔑 API 키 발급 가이드](#-api-키-발급-가이드) |
| 만들어진 엔티티로 예쁜 카드를 만들고 싶다면 | [🎨 대시보드 예제](#-대시보드-예제) |
| 안 되는 게 있으면 | [❓ 자주 묻는 질문](#-자주-묻는-질문-faq) → [🐛 문제 해결](#-문제-해결) |

> 💡 **모든 서비스는 무료**입니다. 정부·공공기관이 제공하는 무료 OpenAPI를 사용하며, 본 컴포넌트는 결제·과금이 일절 없습니다. 일부 서비스(KEPCO/아리수/가스앱)는 본인 계정으로 로그인해야 자신의 사용량을 볼 수 있습니다.

---

## 💡 왜 만들었나?

그동안 한국 사용자가 Home Assistant에 연동하고 싶은 한국 서비스들은 **여러 사람의 개별 custom_component로 흩어져 있었습니다** — 한전 따로, 아리수 따로, 안전알림 따로, 약국 따로, 학교 급식 따로. 각각 설치 방식, 설정 형식, 업데이트 주기, 인증 처리가 제각각이라 관리가 번거롭고, 일부는 유지보수가 멈춘 채 깨지기도 합니다.

본 프로젝트는 **이 흩어진 한국 통합들을 하나의 패키지로 묶었습니다** — 단일 HACS 등록, 단일 config flow UI, 단일 코드베이스. 새 한국 서비스가 필요해지면 여기에 추가하기만 하면 됩니다.

<details>
<summary><b>🇬🇧 English summary (click to expand)</b></summary>

A Home Assistant custom integration exposing 13 Korea-only public services as native entities (sensors, binary sensors, events, calendars, weather).

**Supported services**

| Category | Service | What it does |
|---|---|---|
| Utility | ⚡ **KEPCO** (한국전력) | Current usage, last/predicted monthly bill (login required) |
| Utility | 💧 **Arisu** (서울시 상수도) | Seoul tap-water bill and usage |
| Utility | 🏠 **GasApp** (가스앱) | Monthly city-gas usage and bill (mobile-app token extraction required) |
| Safety | 🚨 **Disaster Alert** (재난문자) | Government emergency alerts, filtered by 시도 (required) + 시군구 (optional) |
| Safety | 📢 **Safety Alert** (안전알림서비스) | Region-based safety bulletins |
| Safety | 🌪️ **Weather Warning** (기상특보) | KMA advisories/warnings as event entities |
| Safety | 🌍 **Earthquake** (지진) | Earthquake alerts with radius / minimum-magnitude filters |
| Weather/Env | ⛅ **KMA Weather** (기상청 동네예보) | Short-term + mid-term forecast as a native `weather` entity |
| Weather/Env | 🌫️ **AirKorea** (에어코리아) | PM10/PM2.5/O₃/NO₂/SO₂/CO + UV/heat/cold living indices |
| Living | 💊 **Pharmacy** (약국) | Pharmacies near you with hours and "open now" flag |
| Living | ⛽ **Fuel** (유가) | Opinet province-level average prices and lowest-price stations |
| Living | 🏫 **School** (학교) | NEIS school meals, academic calendar, class schedule |
| Living | 🚌 **Transit** (대중교통) | Real-time subway and bus arrivals (Seoul + KakaoMap) |

**Optional LLM integration** — every service ships with an LLM tool so you can query it from a voice assistant or chat-style frontend in natural Korean (e.g. "지금 미세먼지 어때?", "가까운 영업중 약국 알려줘").

Aimed at Korean residents (and Korean expats) who want all of the above inside Home Assistant. Most providers do not publish official APIs, so several services use authenticated web scraping — see the Disclaimer section.

Installation and configuration details are in the Korean sections below.

</details>

---

## 📋 지원 서비스

총 **13가지 서비스** · 카테고리별 정리.
각 서비스 박스의 **🎁 등록하면 생기는 것** 항목은 "이 항목을 추가했을 때 실제로 어떤 entity가 만들어지는지"를 보여줍니다. *(엔티티명은 등록한 지역·계정에 따라 자동으로 만들어지며 아래 예시와 비슷한 형태입니다.)*

### 🏠 생활 유틸리티

#### ⚡ 한국전력공사 (KEPCO)
- **전력 사용량** 실시간 모니터링 + **요금 정보**
- 한전 홈페이지 ID/비밀번호 인증 (API 키 ❌, 본인 계정 필요)
- **🎁 등록하면 생기는 것:** 기기 `한전 (사용자ID)` 아래에 다음 5개 sensor —
  - `고객번호`, `전력구분`, `지난달 요금` (원), `예상 요금` (원), `현재 사용량` (kWh)
- **이런 분께 추천:** 예상 요금이 일정 금액을 넘으면 알림을 받고 싶은 분, 월 사용량 그래프를 그리고 싶은 분

#### 💧 아리수 (서울시 상수도)
- **수도요금** 및 사용량 조회
- **수용가번호 + 고객명** 기반 인증 (API 키 ❌, 서울시 거주자만)
  - 수용가번호는 종이 고지서 또는 [아리수 사이버 고객센터](https://i-arisu.seoul.go.kr) 로그인 후 `요금조회/납부 → 수도요금 조회` 화면 좌측에서 확인할 수 있습니다.
- **🎁 등록하면 생기는 것:** 기기 `아리수 (수용가번호)` 아래에 sensor 3개 —
  - `수도 요금` (원), `사용량` (㎥), `청구월`
- **이런 분께 추천:** 가족 사용량을 매월 추적하고 싶은 서울 거주자

#### 🏠 가스앱 (도시가스)
- **가스 사용량** 및 요금 조회
- **토큰 + 회원 ID + 사용계약번호** 인증 (API 키 ❌, 가스앱 모바일 앱 사용자)
- **⚠️ 입력값 추출이 까다롭습니다** — 가스앱은 공식 OpenAPI가 아닌 모바일 앱 내부 API를 사용하기 때문에, **사용계약번호** 외에는 패킷 캡처로 토큰을 추출하는 방식입니다. 패킷 캡처가 부담스러우면 다른 서비스를 권장합니다.
  - **사용계약번호** — 가스앱 모바일 앱 → "내 정보" → 등록된 계약번호 (또는 가스 고지서에 인쇄)
  - **토큰 / 회원 ID** — 가스앱 모바일 앱의 HTTPS 요청 헤더 `X-Token`, `X-Member` 값. mitmproxy/Charles 같은 도구로 추출
- **🎁 등록하면 생기는 것:** 기기 `가스앱 (사용계약번호)` 아래에 sensor 2개 —
  - `청구 제목`, `총 요금` (원)
- **이런 분께 추천:** 동절기 가스비 폭증을 미리 잡고 싶은 분 (단, 추출 작업 가능자)

### 🚨 안전 · 재난

#### 📢 재난문자 (행정안전부 안전데이터포털)
- **재난문자** 실시간 수신
- **광역 시도 (필수) + 시군구 (선택)** 단위 필터링 — config flow가 17개 광역 dropdown + 전국 시군구 평면 dropdown 두 단계로 제공
- **안전데이터포털 (`safetydata.go.kr`)** 인증키 필요 — *공공데이터포털과 다른 별도 포털입니다*
- **🎁 등록하면 생기는 것:** 기기 `재난문자 - <지역>` 아래에 —
  - sensor `최신 재난문자` (state = 가장 최근 메시지 본문, attrs = `level`/`area`/`disaster_type`)
  - sensor `재난문자 수`
  - event `재난문자 이벤트` (새 메시지 도착 시 자동화 트리거)
- **이런 분께 추천:** 핸드폰 알림과 별개로 거실 태블릿/허브에 띄우고 싶은 분, 특정 지역(부모님 댁 등)을 따로 모니터링하고 싶은 분

#### 🚨 안전알림서비스 (행정안전부)
- 지역 기반 **안전 알림 bulletin** (`safekorea.go.kr` 페이지 직접 스크래핑)
- **별도 API 키 / 별도 회원가입 없이** 지역만 선택하면 작동 ✅ *(API 키 신청이 부담스럽다면 여기서 시작하세요)*
- **🎁 등록하면 생기는 것:** 기기 `안전알림 (<지역명>)` 아래에 —
  - sensor `최신 안전알림` (state = 최근 메시지 본문, attrs = `latest`/`alerts[]`/`count`)
  - sensor `안전알림 수`
  - binary_sensor `오늘 안전알림 여부`
  - event `안전알림 이벤트`
- **이런 분께 추천:** 처음 컴포넌트를 체험해보고 싶은 분

#### 🌪️ 기상특보 (기상청)
- **호우 / 강풍 / 한파 / 폭염** 등 12종 특보를 `event` 엔티티로 노출
- 특보 발효 / 해제 / 사전 예고 단계까지 추적
- **기상청_기상특보 통보문 조회 서비스** 키 필요 (`data.go.kr`)
- **🎁 등록하면 생기는 것:** 기기 `기상특보 - <지역>` 아래에 특보 종류별 event 엔티티 12개 —
  - `호우 특보`, `강풍 특보`, `한파 특보`, `폭염 특보`, `대설 특보`, `황사 특보`, `건조 특보`, `풍랑 특보`, `폭풍해일 특보`, `쓰나미 특보` 등
  - 각 event의 state는 `advisory`/`warning`/`pre_advisory`/`pre_warning`/`cancelled`/`none` 중 하나
- **이런 분께 추천:** 폭염 경보가 뜨면 에어컨 자동 가동 같은 자동화를 만들고 싶은 분

#### 🌍 지진 (기상청)
- **반경(km) + 최소 규모(M)** 필터로 알림
- 위/경도 기준으로 거리 자동 계산
- **기상청_지진정보 조회서비스** 키 필요 (`data.go.kr`)
- ⚠️ **기본 좌표는 서울시청 (`37.5665`, `126.978`)** 입니다. 우리 집 좌표로 꼭 바꿔주세요. 기본 반경은 200km, 기본 최소 규모는 3.0 — 알림을 더 잘 받고 싶으면 반경↑/규모↓로 조정
- **🎁 등록하면 생기는 것:** 기기 `지진 정보` 아래에 —
  - event `지진 경보` (state = 가장 최근 지진 시각, 이벤트 발생 시 `magnitude`/`location`/`distance_km`/`datetime` 전달)
  - 추가로 지진별 geolocation 엔티티가 지도 카드에 핀으로 표시됨
- **이런 분께 추천:** 우리 집에서 100km 이내 규모 3.0 이상만 알림 받고 싶은 분

### ⛅ 환경 · 날씨

#### ⛅ 기상청 동네예보 (KMA)
- **단기 + 중기 예보**를 native `weather` 엔티티로 노출
- 시도 → 시군구 다단계 선택, 다중 지역 동시 등록 가능
- 옵션: O₃ / UV는 인근 에어코리아 측정소 자동 매칭
- **기상청_단기예보 ((구)_동네예보) 조회서비스** 키 필요 (`data.go.kr`)
- **🎁 등록하면 생기는 것:** 기기 `기상청 날씨예보 - <지역>` 아래에 `weather` 엔티티 1개 (HA 기본 Weather 카드에 바로 사용 가능, hourly/daily forecast 서비스 지원)
- **이런 분께 추천:** HA 기본 날씨 카드를 한국 기상청 데이터로 채우고 싶은 분

#### 🌫️ 에어코리아 (AirKorea)
- **PM10 / PM2.5 / O₃ / NO₂ / SO₂ / CO + 통합대기질지수(KHAI)** 시계열
- **자외선지수 / 대기정체지수** 등 생활기상지수 추가 등록 가능
- 측정소 단위 다중 등록
- **한국환경공단_에어코리아 대기오염정보** 키 필요 (`data.go.kr`). 생활지수는 별도 **기상청_생활기상지수 조회서비스 V4** 키 추가 입력 시 활성화
- **🎁 등록하면 생기는 것:** 측정소마다 기기 `에어코리아 - <측정소>` 가 만들어지고, 그 아래에 —
  - sensor `PM10 미세먼지` · `PM2.5 초미세먼지` · `SO₂ 아황산가스` · `CO 일산화탄소` · `O₃ 오존` · `NO₂ 이산화질소` · `통합대기질지수`
  - binary_sensor `대기질 경보`, event `대기질 경보 이벤트`, calendar `대기질 예보`
  - (생활지수 키 입력 시) sensor `자외선지수`, `대기정체지수`
- **이런 분께 추천:** 미세먼지 수치에 따라 환기/공기청정기 자동화를 만들고 싶은 분

### 💊 생활 정보

#### 💊 약국 (응급의료정보 — data.go.kr)
- **시도/시군구별** 약국 목록과 영업시간
- `open_now` 동적 계산 (요일·시각 기반) — 지금 영업중인지 자동 판단
- 가까운 순 정렬에 쓸 수 있는 좌표 attribute 포함
- **국립중앙의료원 응급의료기관/약국 정보 조회 서비스** 키 필요 (`data.go.kr`, 운영기관 코드 B552657)
- **🎁 등록하면 생기는 것:** 기기 `약국 - <시군구 or 시도>` 아래에 sensor `운영 약국 수` 1개. attribute에 다음 정보가 들어있어 대시보드용으로 풍부 —
  - `pharmacies[]` (최대 50개; 각 항목: `name`, `address`, `phone`, `today_hours`, `open_now`, `duty_time`, `lat`, `lon`)
  - `total` · `shown` · `open_now_count`
- **이런 분께 추천:** 일요일·공휴일에 가까운 영업 약국을 한눈에 보고 싶은 분, 카카오맵 길찾기 카드를 만들고 싶은 분

#### ⛽ 유가 (Opinet)
- **시도 + 유종**(휘발유/경유/LPG/고급휘발유/등유)별 평균가·최저가
- 시도 내 **최저가 주유소 Top 5 랭킹** attribute
- Opinet API 키 필요 (`opinet.co.kr`)
- **🎁 등록하면 생기는 것:** 등록한 (시도 × 유종) 조합마다 기기 `유가정보 - <지역> <유종>` 아래에 sensor 2개 —
  - `전국 평균가` (원/L)
  - `최저가` (원/L) — attrs: `station_name`, `address`, `ranking[]` (상위 5개 주유소 이름·가격·주소)
- **이런 분께 추천:** 출퇴근 동선 위의 최저가 주유소를 자동으로 추천받고 싶은 분

#### 🏫 학교 (NEIS — 나이스 교육정보 개방 포털)
- **학교 정보 + 급식 + 학사일정 + 시간표** 종합
- **NEIS 교육정보 개방 포털** API 키 필요 (`open.neis.go.kr`)
- **설정 흐름** *(전부 GUI 단계별 안내)*:
  1. API 키 + 학교 급(초/중/고/특수) 선택
  2. 학교명 입력 (예: "한솔초") → 자동으로 검색 결과 dropdown 표시 (최대 10개) → 선택
  3. 학년-반 멀티 선택 (예: `2학년 3반`, `2학년 4반` 동시 등록 가능)
  4. 1~7교시 + 점심 시간 입력
  - 자녀가 둘 이상이면 같은 흐름을 학교마다 반복 등록 가능
- **🎁 등록하면 생기는 것:** 기기 `<학교명>` 아래에 —
  - sensor `급식` (state = 오늘 급식 메뉴 쉼표 구분, attrs: `menu`, `calorie`, `allergy_codes`)
  - sensor `학교 정보` (state = 학교명, attrs: 학년·반·주소·전화)
  - 추가로 학사일정/시간표 calendar 엔티티
- **이런 분께 추천:** 아침에 자녀에게 "오늘 급식 뭐야?" 음성 응답을 시키고 싶은 분

#### 🚌 대중교통 (Transit)
- **지하철 실시간 도착정보** (서울 열린데이터광장)
- **버스 실시간 도착정보** (국토부 + 카카오맵 정류장 ID)
- TIMESTAMP 기반 도착 sensor — 등록한 역/정류장마다 다음 2대까지 표시
- 서울 API 키 + 국토부 버스 API 키 필요
- **설정 흐름**:
  1. 두 API 키 입력
  2. 메뉴에서 "지하철 역 추가" 또는 "버스 노선 추가" 선택
  3. **지하철** — 역 이름 + 방향(상행/하행) + 호선 필터
  4. **버스** — 카카오맵 정류장 ID 입력 → 해당 정류장에 정차하는 노선들이 자동으로 표시 → 추적할 노선 멀티 선택
- 📍 **카카오맵 정류장 ID 찾는 법** — PC에서 [카카오맵](https://map.kakao.com) 접속 → 정류장 이름 검색 → 정류장을 클릭하면 URL이 `https://map.kakao.com/?busstopid=03171&...` 형태로 바뀌는데, **`busstopid=` 뒤의 값**(예: `03171`, `BS09013700`, `223000122` 등)을 복사해서 입력
- **🎁 등록하면 생기는 것:** 지하철은 역·방향별 기기 아래에 도착 sensor 2개(첫 차/다음 차), 버스 정류장은 노선별로 도착 sensor 2개. state는 도착 시각 timestamp (HA가 자동으로 "N분 후"로 표시)
- **이런 분께 추천:** "다음 버스 5분 후 도착하면 우산 알림" 같은 자동화를 만들고 싶은 분

> 📌 **entity_id 표기 안내** — 위 박스의 "sensor `이름`" 형태는 HA에서 표시되는 **친화 이름(friendly name)** 입니다. 실제 entity_id는 HA가 디바이스명·엔티티명을 한글→로마자 슬러그화해서 자동 생성하므로(예: `sensor.yaggug_gangnamgu_unyeong_yaggug_su`), 정확한 ID는 **개발자 도구 → 상태**에서 친화 이름으로 검색해 확인하세요. UI에서 자유롭게 entity_id를 더 직관적인 이름으로 변경할 수도 있습니다.

---

## 🚀 5분 만에 시작하기 (API 키 필요 없음)

처음이라 **뭐가 되는지 일단 확인해보고 싶으시면** 아래 순서대로 따라오세요. API 키 신청 없이 5분이면 첫 sensor가 만들어집니다.

### Step 1. 컴포넌트 설치 (2분)

위쪽의 **`MY` HACS 원클릭 버튼**을 누르세요. 안 보이면 [HACS 설치 방법](#-설치-방법) 참고.

### Step 2. 안전알림 등록 (1분) — **API 키 불필요**

1. **설정 → 기기 및 서비스 → 통합 구성요소 추가**
2. 검색창에 **`한국 컴포넌트 키트`** 입력 *(영문 도메인명 `kr_component_kit` 으로도 검색됩니다)*
3. 13개 서비스 메뉴 중 **🚨 안전알림** 선택
4. 시도/시군구 dropdown에서 한 곳 이상 선택 → **제출**

### Step 3. 결과 확인 (30초)

**개발자 도구 → 상태** 창을 열고 친화 이름으로 `최신 안전알림` 을 검색하세요 — 등록한 지역마다 하나씩 잡힙니다. 클릭하면 자동 생성된 entity_id(예: `sensor.anjeon_allim_seoul_teugbyeolsi_choesin_anjeon_allim`)와 state(가장 최근 행안부 안전 메시지) 가 보입니다. 대시보드에는 다음 한 줄로 표시 —

> 🔍 **"개발자 도구" 위치** — HA 사이드바 하단의 🛠️ 망치 아이콘. 사이드바가 접혀있다면 좌측 위 ☰ 메뉴 → 개발자 도구. (관리자 계정에서만 보입니다.)

```yaml
type: entity
entity: sensor.<copy_paste_from_dev_tools>
```

> 💡 entity_id가 길고 헷갈리면 **설정 → 기기 및 서비스 → "한국 컴포넌트 키트" → 해당 안전알림 카드 → 엔티티 클릭 → 설정(⚙️)** 에서 더 짧은 이름으로 바꿀 수 있습니다 (예: `sensor.safety_alert_gangnam`).

### Step 4. 마음에 들면 추가 등록

같은 통합 구성요소에서 **"항목 추가"** 를 눌러 약국·기상청·재난문자·학교 등을 하나씩 더 등록하세요. 이때 비로소 API 키가 필요해집니다 → [🔑 API 키 발급 가이드](#-api-키-발급-가이드)로 이동.

---

## 🤖 LLM API 연동 (옵션)

각 서비스는 동일한 이름의 **LLM 도구**를 함께 등록합니다. Home Assistant의 **Assist + LLM 통합**(OpenAI / Google / Ollama 등)에 본 통합을 노출하면 자연어로 직접 질의할 수 있습니다.

| 서비스 | 자연어 예시 |
|---|---|
| 약국 | "지금 영업중인 가까운 약국 알려줘" |
| 에어코리아 | "오늘 미세먼지 어때?" |
| 기상청 | "내일 비 와?" |
| 재난문자 | "최근 재난문자 뭐 있어?" |
| 지진 | "최근 지진 있었어?" |
| 학교 | "오늘 급식 뭐야?" |
| 유가 | "우리 동네 휘발유 최저가 어디야?" |
| 대중교통 | "다음 마을버스 언제 와?" |

LLM에서 본 통합을 노출하지 않으면 그냥 일반 sensor/event/weather 엔티티로만 동작합니다. 추가 설정 불필요.

---

## 🚀 설치 방법

### 🎯 HACS가 처음이라면

**HACS(Home Assistant Community Store)** 는 공식 통합에는 없는 사용자 제작 컴포넌트를 GUI로 설치·업데이트할 수 있게 해주는 부가 도구입니다. 한국 서비스처럼 공식에 없는 통합을 쓰려면 거의 필수입니다.

- HACS 자체 설치가 안 되어 있다면 → [HACS 공식 설치 가이드](https://www.hacs.xyz/docs/setup/download/) 먼저 진행 (5~10분)
- 이미 HACS가 있다면 → 아래 세 가지 방법 중 하나를 고르세요

> ℹ️ 본 컴포넌트는 현재 **HACS 사용자 지정 리포지토리(Custom Repository)** 로 설치합니다. HACS Default 등록은 진행 중이며, 등록이 완료되면 별도의 리포지토리 추가 없이 HACS 검색만으로 설치할 수 있게 됩니다.

### 방법 A. **원클릭 설치** (가장 빠름)

페이지 상단의 **`MY` 뱃지**를 누르면 자신의 Home Assistant가 자동으로 열리며 HACS 등록 화면으로 이동합니다. **DOWNLOAD** 클릭 → **Home Assistant 재시작** 만 하면 끝.

> 🔗 [원클릭 설치 링크](https://my.home-assistant.io/redirect/hacs_repository/?owner=redchupa&repository=kr_component_kit&category=integration)

### 방법 B. HACS 안에서 수동 등록

1. Home Assistant 사이드바 → **HACS**
2. 우측 상단 **⋮** (점 3개) 메뉴 → **사용자 지정 리포지토리 (Custom repositories)**
3. 다음 정보 입력:
   - **리포지토리:** `redchupa/kr_component_kit`
   - **카테고리(타입):** `Integration`
4. **추가** 클릭 → HACS 검색에서 **KR Component Kit** 검색 → **DOWNLOAD**
5. **설정 → 시스템 → 다시 시작** 으로 Home Assistant 재시작

### 방법 C. HACS 없이 수동 설치 (비추천)

HACS를 못 쓰는 환경에서만 사용하세요. 이 방법은 **자동 업데이트가 안 됩니다.**

1. 이 리포지토리를 ZIP으로 다운로드 → 압축 해제
2. `custom_components/kr_component_kit` 폴더 전체를 Home Assistant `config/custom_components/` 안에 복사
3. Home Assistant 재시작

> ✅ 설치 확인: 재시작 후 **설정 → 기기 및 서비스 → 통합 구성요소 추가** 에서 `한국 컴포넌트 키트` 가 검색되면 성공입니다. *(HA 검색은 한글 입력 가능 — 안 되면 영문 도메인 `kr_component_kit` 으로도 검색됩니다.)*

---

## ⚙️ 설정 방법

### 기본 흐름

1. **설정 → 기기 및 서비스**
2. 우측 하단 **+ 통합 구성요소 추가** 클릭
3. 검색창에 **`한국 컴포넌트 키트`** 입력 → 선택 *(한글 키보드가 아니면 영문 도메인명 `kr_component_kit` 으로도 검색됩니다)*
4. **13가지 서비스 중 하나** 를 고른 뒤 → 안내 화면에 따라 필요한 정보 입력 → 완료
5. 다른 서비스를 추가하고 싶다면, **이미 등록된 "한국 컴포넌트 키트" 카드 위의 "+ 항목 추가" 버튼** 을 누르세요 (또는 카드의 ⋮ → 항목 추가)
6. 등록 후에 **API 키만 바꾸고 싶다거나 지역을 추가**하고 싶을 때는 해당 항목의 **"구성"** 버튼을 누르면 입력값을 다시 편집할 수 있습니다 (재등록 불필요)

> 💡 한 통합으로 13가지 서비스를 모두 다루므로 **서비스마다 별도로 항목을 추가**하면 됩니다. 같은 서비스를 여러 지역/계정으로 **중복 등록**(예: 본가 + 처가 약국 둘 다)하는 것도 가능합니다.

> 📌 **순서 팁** — API 키가 필요한 서비스는, 먼저 [🔑 API 키 발급 가이드](#-api-키-발급-가이드)에서 키를 받아 클립보드에 복사해둔 뒤 등록하면 가장 빠릅니다.

### 🏠 생활 유틸리티

| 서비스 | 필요한 정보 |
|---|---|
| ⚡ **KEPCO** | 한전 홈페이지 사용자 ID / 비밀번호 |
| 💧 **아리수** | 수용가번호 / 고객명 |
| 🏠 **가스앱** | 토큰 / 회원 ID / 사용계약번호 (모바일 앱에서 추출) |

### 🚨 안전 · 재난

| 서비스 | 필요한 정보 |
|---|---|
| 📢 **재난문자** | `safetydata.go.kr` 인증키 / 광역시도(필수) / 시군구(선택) |
| 🚨 **안전알림** | 광역시도 + 시군구 다중 선택 (서울은 자치구 단위) |
| 🌪️ **기상특보** | `data.go.kr` 서비스 키 / 광역시도 코드 다중 선택 |
| 🌍 **지진** | `data.go.kr` 서비스 키 / 위도·경도 / 반경(km, 기본 200) / 최소 규모(기본 3.0) |

### ⛅ 환경 · 날씨

| 서비스 | 필요한 정보 |
|---|---|
| ⛅ **기상청 동네예보** | `data.go.kr` 서비스 키 / 시도 → 시군구 (옵션: 인근 에어코리아 측정소) |
| 🌫️ **에어코리아** | `data.go.kr` 서비스 키 / 시도 → 측정소 다중 선택 (옵션: 생활지수 키) |

### 💊 생활 정보

| 서비스 | 필요한 정보 |
|---|---|
| 💊 **약국** | `data.go.kr` 서비스 키 / 시도 → 시군구 |
| ⛽ **유가** | Opinet API 키 / 시도 다중 + 유종 다중 |
| 🏫 **학교** | NEIS API 키 / 학교급 → 학교 검색 → 학년·반 → 교시 시간 |
| 🚌 **대중교통** | 서울 API 키 + 국토부 버스 API 키 → 지하철역 / 카카오맵 정류장 ID 추가 |

---

## 🔑 API 키 발급 가이드

대부분의 한국 공공 서비스는 **무료** 인증키만 있으면 사용할 수 있지만, **포털과 데이터셋이 서비스마다 다르기 때문에** 한 번에 헷갈리기 쉽습니다. 아래 표 → 상세 안내 순서로 정리했습니다.

### 한눈에 보기 — 어디서 뭘 받아야 하는가?

> ℹ️ 아래 "신청할 데이터셋" 열에는 포털에서 검색할 때 쓰는 **키워드**와 운영기관·식별번호를 함께 적어두었습니다. 정확한 등록명은 가끔 바뀌므로 **검색어**로 찾는 것이 안전합니다.

| 사용할 서비스 | 발급 포털 | 검색 키워드 / 운영기관 |
|---|---|---|
| 💊 **약국** | [공공데이터포털](https://www.data.go.kr) | `응급의료` 또는 `약국` · 국립중앙의료원 · 서비스 ID `B552657/ErmctInsttInfoInqireService` |
| 📢 **재난문자** | [행정안전부 안전데이터포털](https://www.safetydata.go.kr) | `재난문자` · 식별번호 `DSSP-IF-00247` |
| 🌪️ **기상특보** | [공공데이터포털](https://www.data.go.kr) | `기상특보` 또는 `기상특보 통보문` · 기상청 · `1360000/WthrWrnInfoService` |
| 🌍 **지진** | [공공데이터포털](https://www.data.go.kr) | `지진정보` · 기상청 · `1360000/EqkInfoService` |
| ⛅ **동네예보** | [공공데이터포털](https://www.data.go.kr) | `단기예보` 또는 `동네예보` · 기상청 · `1360000/VilageFcstInfoService_2.0` |
| 🌫️ **에어코리아** | [공공데이터포털](https://www.data.go.kr) | `대기오염정보` · 한국환경공단 · `B552584` (필수) <br> + (옵션) `생활기상지수` · 기상청 · `LivingWthrIdxServiceV4` |
| ⛽ **유가** | [Opinet 오피넷](https://www.opinet.co.kr/user/api/empApiInfo.do) | 무료 회원가입 → API 신청 (포털과 별개) |
| 🏫 **학교** | [NEIS 교육정보 개방 포털](https://open.neis.go.kr) | 회원가입 → 신청 → 인증키 발급 (포털과 별개) |
| 🚌 **대중교통(지하철)** | [서울 열린데이터광장](https://data.seoul.go.kr) | `지하철 실시간 도착정보` |
| 🚌 **대중교통(버스)** | [공공데이터포털](https://www.data.go.kr) | `버스도착정보` 또는 `TAGO` · 국토교통부 |

> ⚠️ **가장 자주 발생하는 실수**
> - **재난문자 키 ≠ 약국 키.** 두 포털(`safetydata.go.kr` vs `data.go.kr`)이 다릅니다.
> - 같은 `data.go.kr` 안에서도 **데이터셋마다 활용신청을 따로** 해야 합니다. 약국 신청한 키로 기상특보가 안 됩니다.
> - 신청 직후에는 키가 활성화되기까지 **1~2시간** 걸릴 수 있습니다(특히 data.go.kr 운영기관 키).

---

### 💊 약국 — 가장 자주 묻는 항목

약국 데이터는 **국립중앙의료원(NMC)**이 제공하며 **공공데이터포털(data.go.kr)**에서 받습니다. 같은 NMC 서비스 안에 응급실·외상센터·약국이 함께 묶여 있어서, 검색 결과의 이름이 "응급의료기관…" 으로 표시되더라도 그게 맞습니다.

**단계별 안내:**

1. **공공데이터포털 가입** — <https://www.data.go.kr> → 우측 상단 회원가입 (이메일/카카오/네이버 OAuth 가능)
2. **데이터셋 검색** — 상단 검색창에 다음 중 하나로 검색:
   - `응급의료` 또는 `응급의료기관`  ← 가장 잘 검색됨
   - `약국 정보` 또는 `전국 약국`
3. **결과 중 선택** — 운영기관이 **국립중앙의료원**이고 OpenAPI 경로에 **`ErmctInsttInfoInqireService`** 가 포함된 항목(운영기관 코드 `B552657`)을 고르세요. 같은 서비스 안에 약국·응급실 등 여러 endpoint가 묶여 있으며 본 컴포넌트는 그 중 `getParmacyListInfoInqire`를 사용합니다.
4. **활용 신청** 버튼 클릭 → 활용 목적란에 짧게 입력 (예: "Home Assistant 가정용 모니터링")
5. **마이페이지 → 오픈API → 인증키 발급현황** 에서 **일반 인증키(Decoding)** 복사
6. Home Assistant 설정 화면의 약국 항목에 그대로 붙여넣기

> 💡 데이터셋의 정확한 등록명은 포털 측에서 가끔 바뀌므로, **이름보다 운영기관(국립중앙의료원) + 서비스 ID(`B552657/ErmctInsttInfoInqireService`)** 를 기준으로 찾으시는 것이 안전합니다.

**약국 API 관련 주의사항:**

| 증상 | 원인 / 해결 |
|---|---|
| `401 Unauthorized` | 서비스키 자체가 잘못됨 (오타·공백). 마이페이지에서 다시 복사 |
| `403 Forbidden` 또는 `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 키는 맞지만 **해당 데이터셋에 활용 신청을 안 했음.** "마이페이지 → 활용신청 현황"에서 *승인* 상태인지 확인 |
| 신청 직후 안 됨 | 데이터셋이 운영기관 키라 **활성화에 1~2시간** 걸릴 수 있음 |
| Encoding/Decoding 키 둘 다 줘서 헷갈림 | 본 통합은 **둘 다 호환** — 아무거나 붙여넣으면 됩니다 (URL 인코딩은 자동 처리) |

---

### 📢 재난문자 — 별도 포털 (가장 헷갈리는 부분)

재난문자만은 일반 공공데이터포털이 아닌 **행정안전부 안전데이터포털**에서 받습니다.

1. <https://www.safetydata.go.kr> 접속 → 회원가입
2. 상단 검색에서 `재난문자` 검색 → **"재난문자방송 정보 조회 서비스"** (식별번호 `DSSP-IF-00247`)
3. **활용신청 → 인증키 발급**
4. 발급된 키를 Home Assistant 재난문자 항목에 입력

> 💡 안전데이터포털은 같은 정부 시스템이지만 **공공데이터포털과 계정·키가 분리**되어 있습니다. 이미 `data.go.kr` 계정이 있어도 별도 가입이 필요합니다.

---

### 🌪️🌍⛅ 기상청 (특보/지진/동네예보) — 한 키로 OK

기상청 API 3종(기상특보·지진·동네예보)은 **모두 공공데이터포털에서 받지만 데이터셋이 각각 다르므로 활용신청을 3번 해야 합니다.** 인증키 자체는 *내 계정 하나에 발급된 같은 키*를 그대로 사용합니다.

- 검색어: `기상특보`, `지진정보`, `단기예보` (또는 `동네예보`)
- 각각의 데이터셋 페이지에서 **활용신청** → 마이페이지에서 *승인* 확인
- Home Assistant 각 항목에 같은 인증키를 입력

---

### 🌫️ 에어코리아 — 필수 + 옵션

- **필수:** 공공데이터포털에서 `대기오염정보` 검색 → **"한국환경공단_에어코리아_대기오염정보"** 활용신청
- **옵션 (UV·열·한파 생활지수):** `생활기상지수` 검색 → **"기상청_생활기상지수 조회서비스 V4"** 활용신청. 신청 안 해도 미세먼지는 정상 동작합니다.

---

### ⛽ 유가 (Opinet) · 🏫 학교 (NEIS) · 🚌 대중교통

이 셋은 공공데이터포털이 아닌 **각 운영기관 자체 포털**에서 발급합니다. 가입 → 신청 → 즉시 발급(보통) 흐름이며, 가입 외 별다른 절차 없이 무료로 받을 수 있습니다.

- **Opinet** — <https://www.opinet.co.kr/user/api/empApiInfo.do>
- **NEIS** — <https://open.neis.go.kr> (회원가입 후 "신청현황 → 인증키 발급")
- **서울 지하철** — <https://data.seoul.go.kr> ("실시간 지하철 도착정보" 신청)
- **국토부 버스** — 공공데이터포털에서 `TAGO 버스도착정보` 활용신청
- **카카오맵 정류장 ID** *(버스 등록 시)* — [카카오맵](https://map.kakao.com) 에서 정류장을 검색·클릭하면 URL이 `https://map.kakao.com/?busstopid=03171&...` 형태로 바뀝니다. **`busstopid=` 뒤의 값** 을 그대로 복사해 입력하세요 (예: `03171`, `BS09013700`, `223000122`).

---

## 🎨 대시보드 예제

각 sensor가 노출하는 attribute를 활용하면 깔끔한 카드를 만들 수 있습니다. 아래 예제는 모두 **추가 HACS 카드 없이** Home Assistant 기본 카드(`tile`, `markdown`, `entities`)만으로 동작합니다.

### 💊 약국 — 가까운 순 + 영업중 필터 + 카카오맵 길찾기

약국 친화 이름 **"운영 약국 수"** sensor의 `pharmacies` attribute를 활용한 카드입니다. (`entity_id`는 HA가 자동 생성한 슬러그 — 예: 시흥시면 `sensor.yaggug_siheungsi_unyeong_yaggug_su`. 본인 지역 entity_id는 **개발자 도구 → 상태** 에서 `운영 약국 수` 검색 후 확인하세요.) 검색·필터를 위해 헬퍼 두 개를 먼저 만들어주세요:

- **설정 → 헬퍼 → 텍스트** : `input_text.yaggug_geomsaeg` (이름: "약국 검색")
- **설정 → 헬퍼 → 토글** : `input_boolean.yaggug_yeongeobjungman` (이름: "약국 영업중만")

대시보드 YAML(섹션 또는 vertical-stack에 통째로 붙여넣기):

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
        entity: sensor.yaggug_siheungsi_unyeong_yaggug_su  # 본인 entity_id 로 변경
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
      {# 위치 기준 entity — zone.home / person.xxx / device_tracker.xxx 로 변경 가능 #}
      {% set tracker = 'zone.home' %}
      {% set sensor_id = 'sensor.yaggug_siheungsi_unyeong_yaggug_su' %}
      {% set my_lat = state_attr(tracker, 'latitude') | float(0) %}
      {% set my_lon = state_attr(tracker, 'longitude') | float(0) %}
      {% set ph = state_attr(sensor_id, 'pharmacies') or [] %}
      {# input_text 의 빈 상태가 'unknown' 으로 들어오는 경우가 있어 정규화 #}
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

**팁:**
- 위치 기준을 폰 따라가게 하려면 `tracker = 'zone.home'`을 `tracker = 'person.<본인>'` 또는 `tracker = 'device_tracker.<폰>'`로 변경.
- 카카오맵 딥링크는 PC/모바일 모두 작동, API 키 불필요.
- `open_now`는 sensor 갱신과 별개로 markdown이 렌더될 때마다 재계산됩니다 (분 단위는 아니지만 시간 단위로는 충분).

### 사용 가능한 sensor attribute 요약

각 sensor의 **friendly name** 기준으로 정리한 표입니다. 실제 `entity_id`는 한글이 로마자로 슬러그화된 형태이므로 **개발자 도구 → 상태** 에서 친화 이름으로 검색하면 확인할 수 있습니다.

| 통합 | 친화 이름 | 주요 attribute |
|---|---|---|
| 약국 | `운영 약국 수` | `pharmacies[]` (`name`/`address`/`phone`/`lat`/`lon`/`duty_time`/`today_hours`/`open_now`), `total`, `shown`, `open_now_count` |
| 기상특보 | `<호우/강풍/한파/폭염/...> 특보` (event) | `warning_type`, `area`, `start_time`, `end_time` (state = `advisory`/`warning`/`pre_*`/`cancelled`/`none`) |
| 에어코리아 | `PM10 미세먼지`, `PM2.5 초미세먼지`, `O₃ 오존`, `NO₂ 이산화질소`, `SO₂ 아황산가스`, `CO 일산화탄소`, `통합대기질지수` | 등급(`Grade`) attribute 동반. 옵션 키 입력 시 `자외선지수`, `대기정체지수` 추가 |
| 기상청 | (weather 엔티티) | hourly/daily forecast 서비스, 체감온도·이슬점·습도 |
| 유가 | `전국 평균가`, `최저가` | 최저가: `station_name`, `address`, `ranking[]` (Top 5) |
| 학교 | `급식`, `학교 정보` + `calendar.*` | 급식: `menu`, `calorie`, `allergy_codes`. 학교 정보: 학년·반·주소·전화 |
| 재난문자 | `최신 재난문자`, `재난문자 수`, event `재난문자 이벤트` | `level`, `area`, `disaster_type` |
| 안전알림 | `최신 안전알림`, `안전알림 수` + binary + event | `latest`, `alerts[]`, `count` |
| 지진 | event `지진 경보` | event 발생 시 `magnitude`, `location`, `distance_km`, `datetime` |
| 대중교통 | `<역/정류장> <호선/노선> ... 도착` | TIMESTAMP — HA가 자동으로 "N분 후"로 표시 |
| KEPCO | `현재 사용량`, `지난달 요금`, `예상 요금`, `고객번호`, `전력구분` | — |
| 아리수 | `수도 요금`, `사용량`, `청구월` | 수도 요금: `billing_month`, `customer_info`, `arrears_info` |
| 가스앱 | `청구 제목`, `총 요금` | — |

---

## 🔄 업데이트 주기

| 카테고리 | 서비스 | 주기 | 비고 |
|---|---|---|---|
| 유틸리티 | 한전 (KEPCO) | 5분 | 로그인 세션 관리 |
| 유틸리티 | 아리수 | 1시간 | 요금·사용량 |
| 유틸리티 | 가스앱 | 20분 | 토큰 갱신 |
| 안전·재난 | 재난문자 | 5분 | 실시간 알림 |
| 안전·재난 | 안전알림 | 5분 | 실시간 알림 |
| 안전·재난 | 기상특보 | 15분 | event 엔티티 |
| 안전·재난 | 지진 | 10분 | event 엔티티 |
| 환경·날씨 | 기상청 동네예보 | 30분 | weather 엔티티 |
| 환경·날씨 | 에어코리아 | 30분 | 시계열 |
| 생활 | 약국 | 1시간 | open_now는 매 렌더 시 재계산 |
| 생활 | 유가 | 1시간 | Opinet |
| 생활 | 학교 | 6시간 | 일자별 변화 거의 없음 |
| 생활 | 대중교통 — 지하철 | 2분 | 실시간 도착 |
| 생활 | 대중교통 — 버스 | 1분 | 실시간 도착 |

---

## 📋 요구사항

- **Home Assistant** 2023.1.0 이상 (hacs.json 명시)
- **Python** 3.11 이상 (HA 자체 요구사항)
- **인터넷 연결** (각 서비스 API 접근)
- 자동 설치되는 Python 패키지: `curl_cffi>=0.7.0`, `beautifulsoup4>=4.12.0` (manifest.json 정의)

---

## ❓ 자주 묻는 질문 (FAQ)

<details>
<summary><b>Q. 13가지 서비스를 전부 등록해야 하나요?</b></summary>

아니요. **원하는 것만 등록**하시면 됩니다. 통합 추가 화면에서 매번 1개 서비스를 고르는 방식이므로, 필요할 때마다 하나씩 늘려가시면 됩니다. 전혀 등록 안 한 서비스는 어떤 entity도 만들지 않고 리소스도 쓰지 않습니다.

</details>

<details>
<summary><b>Q. 사용료가 드나요? 유료 API가 있나요?</b></summary>

**전부 무료**입니다. 정부·공공기관(공공데이터포털, 기상청, NEIS 등)이 제공하는 OpenAPI를 사용하며, 본 컴포넌트와 모든 API는 무료입니다. 단, 각 API는 **일일 호출 한도**(보통 1만 ~ 100만 회/일)가 있지만 가정용 1인 사용으로 한도를 넘기는 일은 거의 없습니다.

</details>

<details>
<summary><b>Q. API 키 신청이 무서워요. 안 받고 쓸 수 있는 게 있나요?</b></summary>

네, **API 키 없이 바로 되는 서비스**가 4가지 있습니다:
- 🚨 **안전알림** — 행안부 안전알림 (지역만 선택)
- ⚡ **한국전력 / 💧 아리수 / 🏠 가스앱** — 본인 계정으로 로그인 (API 키 아님)

이 4개로 먼저 컴포넌트를 체험해 보시고, 마음에 들면 [🔑 API 키 발급 가이드](#-api-키-발급-가이드)대로 다른 서비스를 추가하시면 됩니다.

</details>

<details>
<summary><b>Q. 서울에 안 사는데 사용 가능한가요?</b></summary>

**대부분 전국 가능**합니다.
- 전국: 약국, 재난문자, 안전알림, 기상청 동네예보, 기상특보, 지진, 에어코리아, 학교, 유가
- **서울만:** 아리수(상수도), 서울 지하철 실시간 도착정보
- 도시가스 회사가 가스앱과 연동되어 있으면 전국 가능

</details>

<details>
<summary><b>Q. 한 가족 안에서 여러 학교 / 여러 약국 지역을 동시에 보고 싶어요.</b></summary>

가능합니다. **같은 서비스를 여러 번 등록**하면 각각 독립적인 기기·entity가 만들어집니다.
- 예: "약국" 서비스를 시흥시 / 안양시 / 부모님 댁 시군구 3번 등록 → 기기 3개 (`약국 - 시흥시`, `약국 - 안양시`, `약국 - 부모님 동네`) 와 각 기기 아래 별도 `운영 약국 수` sensor 가 생성됩니다. (entity_id는 자동으로 로마자 슬러그화되어 `sensor.yaggug_siheungsi_*` 형태가 됩니다.)

</details>

<details>
<summary><b>Q. 데이터는 얼마나 자주 갱신되나요? 실시간인가요?</b></summary>

서비스 성격에 따라 다릅니다. [업데이트 주기 표](#-업데이트-주기) 참고. 빠른 것부터 정리하면:
- **1분 ~ 2분:** 버스/지하철 (실시간 도착)
- **5분:** 재난문자, 안전알림, KEPCO
- **10분 ~ 15분:** 지진, 기상특보
- **20분 ~ 30분:** 가스앱, 기상청 예보, 에어코리아
- **1시간:** 아리수, 약국, 유가
- **6시간:** 학교 (급식·시간표는 일자별 변화가 적음)

> 💡 약국의 `open_now`(지금 영업중인가)는 데이터 갱신과 별개로 **대시보드에 표시될 때마다 시각·요일 기준으로 재계산**됩니다.

</details>

<details>
<summary><b>Q. 핸드폰 알림과 함께 쓰려면 어떻게 해야 하나요?</b></summary>

Home Assistant의 **자동화(Automation)** 와 **Companion 앱 푸시**를 조합하면 됩니다. 가장 단순한 자동화 YAML 예시 두 개입니다. 실제 사용 시 `<...>` 부분만 본인 환경에 맞게 바꾸세요.

```yaml
# 1) 재난문자가 새로 도착하면 핸드폰에 푸시
#    "최신 재난문자" sensor의 state가 바뀔 때마다 발사
automation:
  - alias: "재난문자 푸시"
    trigger:
      - platform: state
        entity_id: sensor.<재난문자_최신_엔티티_id>   # 개발자 도구 → 상태에서 "최신 재난문자" 검색해 복사
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state not in ['없음', 'unknown', 'unavailable'] }}"
    action:
      - service: notify.mobile_app_<폰_이름>
        data:
          title: "🚨 재난문자"
          message: "{{ trigger.to_state.state }}"

# 2) PM2.5 > 35 ㎍/㎥ 이면 거실 TTS + 푸시
  - alias: "미세먼지 나쁨 알림"
    trigger:
      - platform: numeric_state
        entity_id: sensor.<측정소_pm25_엔티티_id>   # "PM2.5 초미세먼지" 검색해 복사
        above: 35
    action:
      - service: tts.cloud_say
        data:
          entity_id: media_player.<스피커_엔티티_id>
          message: "현재 미세먼지 수치가 나쁨 단계입니다. 환기를 자제하세요."
      - service: notify.mobile_app_<폰_이름>
        data:
          message: "PM2.5 {{ states(trigger.entity_id) }} ㎍/㎥"
```

> 💡 **친화 이름 → entity_id 변환법**: HA 사이드바의 🛠️ **개발자 도구 → 상태** 탭에서 검색창에 친화 이름(`최신 재난문자`, `PM2.5 초미세먼지` 등)을 입력하면 좌측에 entity_id가 표시됩니다. 그 ID를 위 YAML의 `<...>` 자리에 붙여넣으세요. HA의 자동화 편집 UI(시각적)에서는 친화 이름으로 바로 선택할 수도 있어 더 편합니다.

자동화 만드는 방법 전반은 [HA 자동화 가이드](https://www.home-assistant.io/docs/automation/) 참고.

</details>

<details>
<summary><b>Q. 등록 후에 API 키를 바꾸거나 지역을 추가/삭제하려면 다시 등록해야 하나요?</b></summary>

아닙니다. **설정 → 기기 및 서비스 → "한국 컴포넌트 키트"** 카드에서 해당 항목 옆 **"구성"** 버튼을 누르면 원래 입력했던 값(API 키·지역·유종·좌표 등)을 그대로 편집할 수 있습니다 (Options Flow 지원). 기존 entity와 자동화 연결은 그대로 유지됩니다.

</details>

<details>
<summary><b>Q. "지금 미세먼지 어때?" 같은 음성 질문도 가능한가요?</b></summary>

네, Home Assistant의 **Assist + LLM 통합** (OpenAI / Google / Ollama 등)에 본 컴포넌트를 노출하면 자연어 질문이 가능합니다. 자세한 예시는 [🤖 LLM API 연동](#-llm-api-연동-옵션) 섹션 참고.

</details>

<details>
<summary><b>Q. 등록한 정보(ID/비밀번호/API 키)는 어디에 저장되나요? 안전한가요?</b></summary>

**Home Assistant 내부 저장소(config 폴더 안 `.storage/`)** 에만 저장되며 외부로 전송되지 않습니다. 입력한 비밀번호는 API 호출 시 해당 서비스(한전·아리수 등)의 공식 로그인 페이지에만 사용됩니다. 자세한 책임 한계는 아래 면책조항 섹션 참고.

</details>

<details>
<summary><b>Q. 한 번 등록한 서비스를 삭제하거나 다시 설정하고 싶어요.</b></summary>

**설정 → 기기 및 서비스 → "한국 컴포넌트 키트"** 카드에 등록된 항목 옆 **⋮ → 삭제** 를 누르면 해당 항목과 그 서비스의 모든 entity가 깔끔하게 제거됩니다. 다시 등록하려면 통합 추가를 반복하시면 됩니다.

> 💡 입력값만 바꾸고 싶다면 **삭제 대신 "구성"** 버튼이 더 편합니다 (entity 유지됨).

</details>

<details>
<summary><b>Q. 신축 아파트인데 시군구 목록에 내 동이 없어요.</b></summary>

행정구역 코드가 신도시 신축 동까지 즉시 반영되지 않는 경우가 있습니다. **가장 가까운 인접 동/구 코드**를 선택해 주세요. 기상청 동네예보는 격자 단위(5km × 5km)이므로 인접 코드를 골라도 실제 날씨는 거의 동일합니다.

</details>

<details>
<summary><b>Q. 업데이트는 어떻게 받나요?</b></summary>

HACS로 설치한 경우, 새 릴리즈가 나오면 **HACS → 통합 → KR Component Kit** 에 빨간 점이 표시됩니다. 클릭 → UPDATE → HA 재시작이면 끝입니다. 기존 설정과 entity는 그대로 유지됩니다.

</details>

---

## 🐛 문제 해결

### 로그인 실패 (KEPCO / 아리수 / 가스앱)
- 웹사이트에서 직접 로그인이 되는지 확인
- 2차 인증(OTP) 설정된 계정은 지원하지 않음
- 가스앱은 토큰이 자주 만료될 수 있음 — 앱에서 다시 발급

### API 키 인증 실패
- 신청 직후 1~2시간 활성화 대기 시간이 있을 수 있음 (특히 `data.go.kr` 운영기관 키)
- `data.go.kr` 안에서는 **데이터셋별로 활용신청이 별도** — 약국 키와 기상특보 키는 같은 인증키여도 *각 데이터셋에 신청 승인*이 따로 필요합니다
- **재난문자만은 `safetydata.go.kr` 별도 포털** — 공공데이터포털 키로는 안 됩니다
- `401`은 키 자체가 잘못된 경우, `403`은 키는 맞지만 해당 데이터셋 활용 신청이 안 된 경우입니다
- 일일 요청 한도(트래픽) 초과도 동일 증상으로 나타나니 마이페이지 통계 확인

### 안전알림 / 재난문자 데이터가 비어있을 때
- 안전알림은 `safekorea.go.kr` 페이지를 스크래핑합니다. 해당 사이트 점검 중이면 일시적으로 빈 결과가 나올 수 있음 → 잠시 후 자동 복구
- 재난문자는 `safetydata.go.kr` API가 정기 점검 중일 수 있음 → [점검 공지](https://www.safetydata.go.kr)에서 확인
- 등록한 지역에 최근 발송된 메시지가 없으면 sensor state가 `없음` 으로 표시됩니다 (정상 동작)

### 데이터 업데이트 안됨
- Home Assistant 로그(**설정 → 시스템 → 로그**)에서 `kr_component_kit` 검색
- 각 서비스 API 장애 여부 확인 (`data.go.kr`, KMA 등은 정기 점검이 잦음)

### 기상청 / 약국 좌표가 안 맞을 때
- 시도 → 시군구 선택 시 **공식 행정구역 코드**를 따르므로, 거주지 코드와 행정구역 코드가 다른 경우(예: 신도시 신축 동) 인접 코드를 선택하시면 됩니다

### 그래도 안 풀린다면 — 어디에 물어보나요?

1. **로그 첨부가 우선** — **설정 → 시스템 → 로그** 에서 `kr_component_kit` 으로 검색해 빨간 줄(에러)을 복사
2. [GitHub Issues](https://github.com/redchupa/kr_component_kit/issues) 에 새 이슈 생성 — 다음 정보를 함께 적어주시면 빠르게 해결됩니다:
   - 어떤 서비스를 등록하려 했는지 (예: "약국 — 서울특별시 강남구")
   - HA 버전 / 이 컴포넌트 버전
   - 로그 에러 메시지 (개인정보·API 키는 가린 후)
   - 시도해본 단계

> 💬 한국어 그대로 작성하셔도 됩니다. 답변도 한국어로 드립니다.

---

## ⚠️ 면책조항

- 이 프로젝트는 일부 서비스에서 공식 API가 아닌 **인증된 웹 스크래핑** 방식을 사용합니다 (KEPCO, 아리수, 가스앱)
- 각 서비스 제공업체의 정책 변경에 따라 동작하지 않을 수 있습니다
- 개인정보(ID/비밀번호/토큰)는 Home Assistant 내부 저장소에만 보관되며 외부로 전송되지 않습니다
- 사용자의 책임 하에 이용해주세요

---

## ⭐ 도움이 되셨다면

오른쪽 상단 **Star ⭐** 버튼을 눌러주세요. 별이 모이면 HACS Default Repository 등록 가능성이 올라가고, 더 많은 한국 사용자가 발견할 수 있게 됩니다.

[![Star History Chart](https://api.star-history.com/svg?repos=redchupa/kr_component_kit&type=Date)](https://star-history.com/#redchupa/kr_component_kit&Date)

---

## ☕ 후원

이 프로젝트가 도움이 되셨다면 커피 한 잔으로 응원해주세요! 🙏

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
