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

## 💡 왜 만들었나?

그동안 한국 사용자가 Home Assistant에 연동하고 싶은 한국 서비스들은 **여러 사람의 개별 custom_component로 흩어져 있었습니다** — 한전 따로, 아리수 따로, 안전알림 따로, 약국 따로, 학교 급식 따로. 각각 설치 방식, 설정 형식, 업데이트 주기, 인증 처리가 제각각이라 관리가 번거롭고, 일부는 유지보수가 멈춘 채 깨지기도 합니다.

본 프로젝트는 **이 흩어진 한국 통합들을 하나의 패키지로 묶었습니다** — 단일 HACS 등록, 단일 config flow UI, 단일 코드베이스. 새 한국 서비스가 필요해지면 여기에 추가하기만 하면 됩니다.

<details>
<summary><b>🇬🇧 English summary (click to expand)</b></summary>

A Home Assistant custom integration exposing 13 Korea-only public services as native entities (sensors, binary sensors, events, calendars, weather).

**Supported services**

| Category | Service | What it does |
|---|---|---|
| Utility | ⚡ **KEPCO** (한국전력) | Real-time electricity usage, bill estimate, progressive-tier indicator |
| Utility | 💧 **Arisu** (서울시 상수도) | Seoul tap-water bill and usage |
| Utility | 🏠 **GasApp** (가스앱) | Monthly city-gas usage and bill |
| Safety | 🚨 **Disaster Alert** (재난문자) | Government emergency alerts, filtered by 시도/시군구/읍면동 |
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

총 **13가지 서비스** · 카테고리별 정리

### 🏠 생활 유틸리티

#### ⚡ 한국전력공사 (KEPCO)
- **전력 사용량** 실시간 모니터링
- **이번달 / 지난달 요금** 및 누진단계
- 한전 홈페이지 ID/비밀번호 인증

#### 💧 아리수 (서울시 상수도)
- **수도요금** 및 사용량 조회
- **고객번호 + 고객명** 기반 인증

#### 🏠 가스앱 (도시가스)
- **가스 사용량** 및 요금 조회
- **토큰 + 회원 ID + 사용계약번호** 인증

### 🚨 안전 · 재난

#### 📢 재난문자 (행정안전부 안전데이터포털)
- **재난문자** 실시간 수신
- **시도 / 시군구 / 읍면동** 단위 필터링
- `data.go.kr`(공공데이터포털) **재난문자 발송정보** 서비스 키 필요

#### 🚨 안전알림서비스 (행정안전부)
- 지역 기반 **안전 알림 bulletin**
- 별도 API 키 없이 등록한 지역만 알림

#### 🌪️ 기상특보 (기상청)
- **호우 / 강풍 / 한파 / 폭염** 등 특보를 `event` 엔티티로 노출
- 특보 발효 / 해제 / 사전 예고 단계까지 추적
- **기상청 단기예보 조회서비스** 키 필요

#### 🌍 지진 (기상청)
- **반경(km) + 최소 규모(M)** 필터로 알림
- 위/경도 기준으로 거리 자동 계산
- **기상청 지진정보 조회서비스** 키 필요

### ⛅ 환경 · 날씨

#### ⛅ 기상청 동네예보 (KMA)
- **단기 + 중기 예보**를 native `weather` 엔티티로 노출
- 시도 → 시군구 다단계 선택, 다중 지역 동시 등록 가능
- 옵션: O₃ / UV는 인근 에어코리아 측정소 자동 매칭

#### 🌫️ 에어코리아 (AirKorea)
- **PM10 / PM2.5 / O₃ / NO₂ / SO₂ / CO** 시계열
- **자외선 / 열·한파 생활지수** 추가 등록 가능
- 측정소 단위 다중 등록

### 💊 생활 정보

#### 💊 약국 (응급의료정보 — data.go.kr)
- **시도/시군구별** 약국 목록과 영업시간
- `open_now` 동적 계산 (요일·시각 기반)
- 가까운 순 정렬에 쓸 수 있는 좌표 attribute 포함

#### ⛽ 유가 (Opinet)
- **시도 + 유종**(휘발유/경유/LPG/고급휘발유)별 평균가·최저가
- 시도 내 **최저가 주유소 목록** attribute

#### 🏫 학교 (NEIS — 나이스 교육정보 개방 포털)
- **학교 정보 / 급식 / 학사일정 / 시간표** 종합
- 학교명 검색 → 학년·반 선택, 교시 시간 직접 설정 가능
- **NEIS 교육정보 개방 포털** API 키 필요

#### 🚌 대중교통 (Transit)
- **지하철 실시간 도착정보** (서울 열린데이터광장)
- **버스 실시간 도착정보** (국토부 + 카카오맵 정류장 ID)
- TIMESTAMP 기반 도착 sensor — 시각·분 단위 표시 모두 가능

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

### HACS를 통한 설치 (권장)

1. **HACS** 메뉴로 이동
2. **통합 구성요소** 선택
3. 우측 상단 **⋮** 메뉴 → **사용자 지정 리포지토리**
4. 다음 정보 입력:
   - **리포지토리**: `redchupa/kr_component_kit`
   - **카테고리**: `Integration`
5. **KR Component Kit** 검색 후 설치
6. **Home Assistant 재시작**

### 수동 설치

1. 이 리포지토리를 다운로드
2. `custom_components/kr_component_kit` 폴더를 Home Assistant의 `custom_components` 디렉토리에 복사
3. Home Assistant 재시작

---

## ⚙️ 설정 방법

**설정** → **기기 및 서비스** → **통합 구성요소 추가** → **"KR Component Kit"** 검색 → 추가하려는 서비스 선택.

> 한 통합으로 13가지 서비스를 모두 다루므로 **각 서비스마다 별도로 항목을 추가**하면 됩니다. 같은 서비스를 여러 지역/계정으로 중복 등록하는 것도 가능합니다.

### 🏠 생활 유틸리티

| 서비스 | 필요한 정보 |
|---|---|
| ⚡ **KEPCO** | 한전 홈페이지 사용자 ID / 비밀번호 |
| 💧 **아리수** | 고객번호 / 고객명 |
| 🏠 **가스앱** | 토큰 / 회원 ID / 사용계약번호 |

### 🚨 안전 · 재난

| 서비스 | 필요한 정보 |
|---|---|
| 📢 **재난문자** | `data.go.kr` 서비스 키 / 시도(필수) / 시군구·읍면동(선택) |
| 🚨 **안전알림** | 시도 + 시군구 다중 선택 |
| 🌪️ **기상특보** | KMA 서비스 키 / 지역 코드 |
| 🌍 **지진** | KMA 서비스 키 / 위도·경도 / 반경(km) / 최소 규모 |

### ⛅ 환경 · 날씨

| 서비스 | 필요한 정보 |
|---|---|
| ⛅ **기상청 동네예보** | KMA 서비스 키 / 시도 → 시군구 (옵션: 인근 에어코리아 측정소) |
| 🌫️ **에어코리아** | 에어코리아 API 키 / 시도 → 측정소 다중 선택 (옵션: 생활지수 키) |

### 💊 생활 정보

| 서비스 | 필요한 정보 |
|---|---|
| 💊 **약국** | `data.go.kr` 서비스 키 / 시도 → 시군구 |
| ⛽ **유가** | Opinet API 키 / 시도 다중 + 유종 다중 |
| 🏫 **학교** | NEIS API 키 / 학교급 → 학교 검색 → 학년·반 → 교시 시간 |
| 🚌 **대중교통** | 서울 API 키 + 국토부 버스 API 키 → 지하철역 / 카카오맵 정류장 ID 추가 |

> 💡 **API 키 발급처**
> - **공공데이터포털 (`data.go.kr`)** — 재난문자, 약국 (응급의료정보)
> - **기상청 API허브 (`apihub.kma.go.kr`)** — 기상특보, 동네예보, 지진
> - **에어코리아 (`airkorea.or.kr`)** — 대기질, 생활지수
> - **Opinet (`opinet.co.kr`)** — 유가
> - **NEIS 교육정보 개방 포털 (`open.neis.go.kr`)** — 학교
> - **서울 열린데이터광장 (`data.seoul.go.kr`)** — 지하철
> - **국토부 (`bus.go.kr` / `data.go.kr`)** — 버스

---

## 🎨 대시보드 예제

각 sensor가 노출하는 attribute를 활용하면 깔끔한 카드를 만들 수 있습니다. 아래 예제는 모두 **추가 HACS 카드 없이** Home Assistant 기본 카드(`tile`, `markdown`, `entities`)만으로 동작합니다.

### 💊 약국 — 가까운 순 + 영업중 필터 + 카카오맵 길찾기

`sensor.약국_<지역>_운영_약국_수`의 `pharmacies` attribute를 활용. 검색·필터를 위해 헬퍼 두 개를 먼저 만들어주세요:

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

| 통합 | 엔티티 | 주요 attribute |
|---|---|---|
| 약국 | `sensor.<지역>_운영_약국_수` | `pharmacies[]` (name/address/phone/lat/lon/duty_time/today_hours/`open_now`), `total`, `open_now_count` |
| 기상특보 | `event.<지역>_<특보>` | `event_type`(advisory/warning/...), `start_time`, `end_time`, `warn_stress` |
| 에어코리아 | `sensor.<측정소>_<오염물질>` | 시계열 `pm10`/`pm25`/`o3`/`no2`/`so2`/`co` + 생활지수 |
| 기상청 | `weather.<지역>` | 단기·중기 예보, hourly/daily forecast 서비스 |
| 유가 | `sensor.<지역>_<유종>_평균가` | `low_price_stations[]`, 시도별 평균/최저 |
| 학교 | `sensor.<학교>_급식` + `calendar.*` | 오늘/내일 메뉴, 알레르기, 학사일정, 시간표 |
| 재난문자 | `sensor.<지역>_재난문자` | 최근 메시지 + count |
| 지진 | `event.<위치>_지진` | 진도/위도/경도/거리 |
| 대중교통 | `sensor.*_도착` | TIMESTAMP, 다음 차량 정보 |
| KEPCO/아리수/가스앱 | `sensor.*` | 사용량, 요금, (KEPCO만) 누진단계 |

각 sensor의 정확한 attribute는 **개발자 도구 → 상태**에서 entity 검색하시면 확인 가능합니다.

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

- **Home Assistant** 2023.1.0 이상
- **Python** 3.11 이상
- **인터넷 연결** (각 서비스 API 접근)
- (대중교통 일부) `curl_cffi` — 자동 설치됨

---

## 🐛 문제 해결

### 로그인 실패 (KEPCO / 아리수 / 가스앱)
- 웹사이트에서 직접 로그인이 되는지 확인
- 2차 인증(OTP) 설정된 계정은 지원하지 않음
- 가스앱은 토큰이 자주 만료될 수 있음 — 앱에서 다시 발급

### API 키 인증 실패
- `data.go.kr` / KMA / Opinet / 에어코리아 / NEIS 키는 **신청 후 활성화까지 시간**이 걸리는 경우가 있음
- `data.go.kr`은 같은 포털이라도 **데이터셋과 활용신청이 1:1 매칭** — 약국 키 ≠ 재난문자 키
- 키가 정확해도 401/403이 반복되면 해당 서비스의 일일 요청 한도 초과 여부 확인

### 안전알림 / 재난문자 지역 목록이 표시되지 않을 때
- 네트워크 연결 상태 점검
- 잠시 후 다시 시도 (서버 일시 장애 가능)
- 지역 목록 로드 실패 시 지역 코드를 직접 입력하는 폴백 화면이 표시됩니다

### 데이터 업데이트 안됨
- Home Assistant 로그(**설정 → 시스템 → 로그**)에서 `kr_component_kit` 검색
- 각 서비스 API 장애 여부 확인 (`data.go.kr`, KMA 등은 정기 점검이 잦음)

### 기상청 / 약국 좌표가 안 맞을 때
- 시도 → 시군구 선택 시 **공식 행정구역 코드**를 따르므로, 거주지 코드와 행정구역 코드가 다른 경우(예: 신도시 신축 동) 인접 코드를 선택하시면 됩니다

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
