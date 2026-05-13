# 🇰🇷 KR Component Kit

> **A Home Assistant integration for Korean residents** — KEPCO electricity, Seoul water, city gas, KMA weather, government disaster alerts, pharmacy info, school meals, real-time public transit, air quality, fuel prices, and earthquake warnings — 13 Korea-only public services bundled in one package.

🇰🇷 [한국어 README](README.md) · 🇬🇧 **English (this page)**

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Stargazers][stars-shield]][stars]

[![Open your Home Assistant instance and open a repository inside the HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=redchupa&repository=kr_component_kit&category=integration)

---

## Why this exists

Korean public services don't have a standard OpenAPI surface like utilities elsewhere. Each agency runs its own portal (`data.go.kr`, `safetydata.go.kr`, `opinet.co.kr`, `open.neis.go.kr`, `data.seoul.go.kr`), with its own signup, its own dataset-by-dataset 활용신청 (use application), and its own quirks.

This integration wraps the 13 most useful Korea-only services into one Home Assistant integration, with a unified config flow, native HA entities (sensors, weather, event, calendar), and an optional LLM tool surface for natural-Korean voice queries.

**Who this is for:**
- Korean residents (citizens, expats, or international residents) running Home Assistant
- Korean expats abroad monitoring family-home utilities or disaster alerts back home
- Anyone integrating Korean weather/air-quality data into a global HA setup

---

## 🚀 5-minute quickstart

### Step 1. Install (2 min)

Click the **`MY` HACS badge** at the top — your Home Assistant opens automatically, lands on the HACS download screen → **DOWNLOAD** → **restart Home Assistant**.

*No HACS yet? → [HACS official setup guide](https://www.hacs.xyz/docs/setup/download/) first.*

### Step 2. Register your first service (1 min) — **no API key needed**

**Settings → Devices & Services → + Add Integration**
→ Search `한국 컴포넌트 키트` *(the Korean name; English domain `kr_component_kit` also works)*
→ Select **🚨 안전알림 (Safety Alert)** → pick 시도 (province) / 시군구 (city/district) / 읍면동 (town) → Submit.

### Step 3. Verify (30 sec)

**Developer Tools → States** → search for the friendly name `최신 안전알림` ("Latest Safety Alert") → state shows the most recent Korean government safety bulletin for your area.

### Step 4. Add more services

When ready, follow the [🔑 API Key Guide](#-api-key-guide) below to add the other 12 services one by one.

---

## 📋 The 13 services at a glance

| Service | Category | API key | Notes |
|---|---|---|---|
| 💊 **Pharmacy** (약국) | Living | ✅ data.go.kr | Pharmacies near you with "open now" flag |
| 🚨 **Safety Alert** (안전알림) | Safety | ❌ none | Government safety alerts (scraping) |
| 📢 **Disaster Alert** (재난문자) | Safety | ✅ safetydata.go.kr | Emergency text broadcasts in real time |
| 🌪️ **Weather Warning** (기상특보) | Safety | ✅ data.go.kr | 12 advisory types (rain, wind, cold, heat…) |
| 🌍 **Earthquake** (지진) | Safety | ✅ data.go.kr | Radius + magnitude filters |
| ⛅ **KMA Forecast** (동네예보) | Weather | ✅ data.go.kr | Native HA Weather card |
| 🌫️ **AirKorea** (에어코리아) | Weather | ✅ data.go.kr (×2) | PM10/PM2.5 + KHAI air-quality index |
| ⚡ **KEPCO** (한국전력) | Utility | ❌ (own login) | Electricity usage + bill |
| 💧 **Arisu** (서울 상수도) | Utility | ❌ (account number) | Seoul tap water only |
| 🏠 **GasApp** (가스앱) | Utility | ❌ (mobile-app token) | Packet capture required (advanced) |
| ⛽ **Fuel** (유가) | Living | ✅ opinet.co.kr | Province-level avg / lowest-price stations |
| 🏫 **School** (학교) | Living | ✅ open.neis.go.kr | Lunch menu, schedule, calendar |
| 🚌 **Transit** (대중교통) | Living | Partial | Subway: Seoul key / Bus: no key (KakaoMap) |

> 💡 **All services are free.** Korean public APIs are gratis; this integration adds no payment of its own.

---

## 🔑 API Key Guide

> ⚠️ **Three common pitfalls**
> - Disaster alerts use `safetydata.go.kr` (Safety Data Portal) — **a different site** from `data.go.kr` (Public Data Portal). Separate signup.
> - Even within `data.go.kr`, each dataset needs **its own 활용신청 (use application)** — a key approved for pharmacies returns 403 when called against weather warnings.
> - After applying, expect **1–2 hours of activation lag** (especially agency-issued keys).

Each "👉 Direct search" link below lands on the portal's search-results page with the Korean keyword pre-filled.

### 💊 Pharmacy (전국 약국 정보)

| Field | Value |
|---|---|
| 🌐 Portal | [Public Data Portal (data.go.kr)](https://www.data.go.kr) |
| 🔎 Direct search | [👉 Open pharmacy search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=전국%20약국) |
| Search keyword | `전국 약국` or `약국 정보` |
| Operating agency | National Medical Center (NMC) — code `B552657` |
| Exact dataset name | **국립중앙의료원_전국 약국 정보 조회 서비스** |
| Endpoint called by code | `apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire` |

**Steps:** Sign up at the portal (Korean OAuth via Naver/Kakao works) → click the direct-search link → pick the dataset → **활용신청** (Use Application) → My Page → Open API → Auth Key list → copy the **Decoding** form → paste into HA pharmacy field.

---

### 📢 Disaster Alert (재난문자)

| Field | Value |
|---|---|
| 🌐 Portal | [Safety Data Portal (safetydata.go.kr)](https://www.safetydata.go.kr) |
| 🔎 Direct search | Search box at top → type `재난문자` |
| Search keyword | `재난문자` |
| Operating agency | Ministry of the Interior and Safety |
| Endpoint | `safetydata.go.kr/V2/api/DSSP-IF-00247` |

> ⚠️ Safety Data Portal and Public Data Portal are **separate sites** even though both are government-run. Sign up separately even if you already have a `data.go.kr` account.

---

### 🌪️ Weather Warning + 🌍 Earthquake + ⛅ Short-term Forecast (3 KMA datasets, same key)

All three live under `data.go.kr`, operating agency **Korea Meteorological Administration (KMA)**, agency code `1360000`. **One auth key per account** — but each dataset still needs its own 활용신청.

| Service | Direct search | Keyword | Endpoint |
|---|---|---|---|
| 🌪️ Weather warning | [👉 Search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=기상특보) | `기상특보` | `1360000/WthrWrnInfoService` |
| 🌍 Earthquake | [👉 Search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=지진정보) | `지진정보` | `1360000/EqkInfoService` |
| ⛅ Short-term forecast | [👉 Search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=단기예보) | `단기예보` | `1360000/VilageFcstInfoService_2.0` |

---

### 🌫️ AirKorea (Air Quality) — **two datasets required**

`data.go.kr`, operating agency **Korea Environment Corporation**, agency code `B552584`. Both datasets must be applied for separately.

| Dataset | Direct search | Keyword | Endpoint |
|---|---|---|---|
| Station info | [👉 Search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=에어코리아%20측정소) | `에어코리아 측정소` | `B552584/MsrstnInfoInqireSvc` |
| Pollution data | [👉 Search](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=에어코리아%20대기오염) | `에어코리아 대기오염` | `B552584/ArpltnInforInqireSvc` |

> 💡 If station-info is missing, the station dropdown in HA setup will be empty.

> ⚠️ **Optional — Living Weather Index (UV / air stagnation)**: code calls the `V4` endpoint, but the portal seems to have moved to `V5`. Live operation unverified. If you want these sensors, search `생활기상지수` and apply; check HA logs (`Settings → System → Logs`, search `LivingWthrIdx`) for actual behavior. PM10/PM2.5 (the required two) are unaffected.

---

### ⛽ Fuel (Opinet)

| Field | Value |
|---|---|
| 🌐 Portal | [👉 Opinet API signup page](https://www.opinet.co.kr/user/api/empApiInfo.do) |
| Process | Free signup → API application → immediate issuance |
| Endpoint | `opinet.co.kr/api/avgAllPrice.do`, `lowTop10.do` |

> 💡 Opinet is a **separate portal** from the Public Data Portal.

---

### 🏫 School (NEIS)

| Field | Value |
|---|---|
| 🌐 Portal | [👉 NEIS Education Open Portal](https://open.neis.go.kr) |
| Process | Sign up → request auth key → check My Page "Application Status" |
| Endpoint | `open.neis.go.kr/hub/...` |

> 💡 NEIS is also a **separate portal**. The HA config flow auto-searches schools by name — just type your school's Korean name into the dropdown.

---

### 🚌 Transit — keys depend on scenario

| Use case | Key needed | Where |
|---|---|---|
| Subway arrivals | Seoul Open Data Plaza key | [👉 data.seoul.go.kr](https://data.seoul.go.kr) → apply for `지하철 실시간 도착정보` |
| Bus arrivals | **None needed** | KakaoMap's unofficial endpoint; just enter the stop ID |
| Transfer path search (optional) | Seoul transfer-route API key | [👉 data.go.kr](https://www.data.go.kr/tcs/dss/selectDataSetList.do?searchKeyword=대중교통환승경로) → `대중교통환승경로` |

**Finding a KakaoMap bus stop ID** *(for bus registration)*:
[KakaoMap](https://map.kakao.com) → search for the stop → click it → URL becomes `?busstopid=03171&...` → **copy the value after `busstopid=`** (e.g., `03171`, `BS09013700`).

---

## ⚙️ Registration & reconfiguration

### Adding a new entry
Settings → Devices & Services → **+ Add Integration** → `한국 컴포넌트 키트` → pick service.

> One integration menus 13 services — add them one at a time. **Same service can be registered multiple times for different regions** (e.g., pharmacy for your district + your in-laws' district = 3 separate entries).

### Changing API keys / regions after setup
The relevant entry's **"Configure"** button → edit. *(No need to delete-and-reregister; entities and automations preserved.)*

### Where to get each non-API-key input

| Service | Where |
|---|---|
| ⚡ **KEPCO** | Your KEPCO website ID / password (2FA not supported) |
| 💧 **Arisu** | Paper bill or [Arisu Cyber Customer Center](https://i-arisu.seoul.go.kr) → 요금조회 (Bill Inquiry) → left sidebar shows 수용가번호 (customer number) + 고객명 (customer name) |
| 🏠 **GasApp** | Contract number from the GasApp mobile app → My Info. Token + member ID via packet capture (mitmproxy / Charles) of the mobile-app HTTPS request headers `X-Token` / `X-Member` (⚠️ advanced) |
| 🌍 **Earthquake coordinates** | Defaults to Seoul City Hall (`37.5665, 126.978`). **Set your home coordinates.** Default radius 200 km / minimum magnitude 3.0 |

---

## 🎁 Entities you'll get

> Entity IDs are auto-romanized from Korean (e.g., device `약국 - 시흥시` + entity `운영 약국 수` → `sensor.yaggug_siheungsi_unyeong_yaggug_su`). To find the exact ID, search by **friendly name** in Developer Tools → States.

| Service | Friendly names | Key attributes |
|---|---|---|
| 💊 Pharmacy | `운영 약국 수` ("Operating Pharmacy Count") | `pharmacies[]` (up to 50: name/address/phone/lat/lon/today_hours/`open_now`/duty_time), `total`, `shown`, `open_now_count` |
| 🚨 Safety Alert | `최신 안전알림`, `안전알림 수`, `오늘 안전알림 여부` (binary), `안전알림 이벤트` (event) | `latest`, `alerts[]`, `count` |
| 📢 Disaster Alert | `최신 재난문자`, `재난문자 수`, `재난문자 이벤트` (event) | `level`, `area`, `disaster_type` |
| 🌪️ Weather Warning | `호우 특보`/`강풍 특보`/`한파 특보`/... (12 event entities) | state: `advisory`/`warning`/`pre_*`/`cancelled`/`none`, `start_time`, `end_time` |
| 🌍 Earthquake | `지진 경보` (event) | `magnitude`, `location`, `distance_km`, `datetime` |
| ⛅ Forecast | Single weather entity — compatible with HA's standard Weather card | hourly/daily forecast service |
| 🌫️ AirKorea | `PM10 미세먼지`, `PM2.5 초미세먼지`, `O₃ 오존`, `NO₂`, `SO₂`, `CO`, `통합대기질지수` + binary `대기질 경보` + event + calendar `대기질 예보` | Grade attribute attached |
| ⚡ KEPCO | `현재 사용량` (kWh), `지난달 요금` (KRW), `예상 요금`, `고객번호`, `전력구분` | — |
| 💧 Arisu | `수도 요금` (KRW), `사용량` (㎥), `청구월` | `billing_month`, `customer_info`, `arrears_info` |
| 🏠 GasApp | `청구 제목`, `총 요금` (KRW) | — |
| ⛽ Fuel | `전국 평균가`, `최저가` (per sido × fuel-type combo) | `ranking[]` (top 5 stations) |
| 🏫 School | `급식` ("Lunch"), `학교 정보` + calendar entities for academic schedule and timetable | Lunch: `menu`, `calorie`, `allergy_codes` |
| 🚌 Transit | `<station/stop> ... 도착` (TIMESTAMP — HA auto-shows "N min later") | — |

---

## 🤖 Natural-language queries (LLM, optional)

If you expose this integration to HA's **Assist + LLM** (OpenAI / Google / Ollama / etc.), you can ask in natural Korean:

| Query | Service |
|---|---|
| "지금 영업중인 가까운 약국 알려줘" ("Find nearby pharmacies open now") | 💊 Pharmacy |
| "오늘 미세먼지 어때?" ("How's the air quality today?") | 🌫️ AirKorea |
| "내일 비 와?" ("Will it rain tomorrow?") | ⛅ KMA |
| "오늘 급식 뭐야?" ("What's for school lunch today?") | 🏫 School |
| "다음 버스 언제 와?" ("When's the next bus?") | 🚌 Transit |

Without LLM exposure, regular sensor/event/weather entities work as normal — no extra setup required.

---

## ❓ FAQ

<details>
<summary><b>Do I have to register all 13 services?</b></summary>

No. Register only what you want. Services you don't register create zero entities and consume no resources.
</details>

<details>
<summary><b>Are any of these paid?</b></summary>

**All free.** Korean government / public-corporation OpenAPIs; this integration adds no cost of its own. Each API has daily call quotas (typically 10,000 – 1,000,000/day) — never an issue for single-household use.
</details>

<details>
<summary><b>I'm intimidated by API key signups. What can I try first?</b></summary>

**Four services work without any API key**:
- 🚨 **Safety Alert** — pick a region (scraping-based)
- ⚡ **KEPCO / 💧 Arisu / 🏠 GasApp** — your own account (not an API key)
</details>

<details>
<summary><b>I live outside Seoul. Does this work?</b></summary>

Most services work nationwide. **Seoul-only**: Arisu (water), Seoul subway real-time arrivals. Everything else is countrywide.
</details>

<details>
<summary><b>How do I change my API key or region after setup?</b></summary>

Settings → Devices & Services → **한국 컴포넌트 키트** card → that entry's **Configure** button → edit. No delete-and-reregister needed; entities + automations preserved.
</details>

<details>
<summary><b>Can I register the same service multiple times for different regions?</b></summary>

Yes. Register the pharmacy service for your district + your in-laws' district + your parents' district — three independent device/entity sets.
</details>

<details>
<summary><b>How do I send phone notifications when an alert comes in?</b></summary>

Combine HA Automation with the Companion app's `notify.mobile_app_*` service. Minimal example:

```yaml
automation:
  - alias: "Disaster alert → phone push"
    trigger:
      - platform: state
        entity_id: sensor.<your_disaster_message_entity>
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state not in ['없음', 'unknown', 'unavailable'] }}"
    action:
      - service: notify.mobile_app_<your_phone>
        data:
          title: "🚨 Disaster Alert"
          message: "{{ trigger.to_state.state }}"
```

Look up entity IDs by friendly name in Developer Tools → States.
</details>

<details>
<summary><b>Where are my credentials stored?</b></summary>

In Home Assistant's internal storage (`.storage/`) only. Passwords are sent only to the respective service's official login page (e.g., KEPCO / Arisu). See [Disclaimer](#️-disclaimer).
</details>

<details>
<summary><b>How do I update?</b></summary>

HACS shows a red dot on **HACS → Integrations → KR Component Kit** when a new release is available. Click → UPDATE → restart HA. Existing config + entities preserved.
</details>

<details>
<summary><b>My new-build apartment isn't in the district dropdown.</b></summary>

Government administrative codes occasionally lag for newly-built areas. Pick the nearest adjacent district. KMA forecasts are 5 km × 5 km grids anyway, so the actual weather data is nearly identical.
</details>

---

## 🔄 Update intervals

| Category | Service | Interval |
|---|---|---|
| Real-time | Bus / Subway | 1–2 min |
| Safety | Disaster, Safety Alert, KEPCO | 5 min |
| Safety | Earthquake, Weather Warning | 10–15 min |
| Environment/Utility | GasApp, KMA Forecast, AirKorea | 20–30 min |
| Living | Arisu, Pharmacy, Fuel | 1 hour |
| Living | School (meals/timetable) | 6 hours |

> 💡 Pharmacy `open_now` (currently open) is **recomputed live each dashboard render** independently of data refresh.

---

## ⚠️ Known limitations (honest disclosure)

Some services use non-official paths (HTML scraping, mobile-app APIs). External-site changes can temporarily break them. All known weak spots:

| Service | Limit |
|---|---|
| 🚨 **Safety Alert / 📢 Disaster Alert** | `safekorea.go.kr` HTML scraping / `safetydata.go.kr` API. May break during government-site maintenance. Disaster Alert uses 5-profile Chrome impersonation rotation; Safety Alert uses single `chrome120` profile |
| ⚡ **KEPCO** | Login-success URL markers are hardcoded — if KEPCO renames its post-login page, detection fails. 2FA not supported. Look for `KEPCO login: unknown redirect` in HA logs to debug |
| 💧 **Arisu** | HTML scraping of `i121.seoul.go.kr` — Seoul city website structure changes can break parsing. Assumes 9-digit customer number |
| 🏠 **GasApp** | Uses the mobile-app internal API. Token extraction requires packet-capture tooling (mitmproxy / Charles) — high barrier for non-technical users |
| 🌫️ **AirKorea Living Index (UV / air stagnation)** | Code calls `V4` endpoint, but the portal seems upgraded to `V5` — live operation unverified. Required pollution datasets are unaffected |
| 🏫 **NEIS** | `INFO-200` (no-data, normal) is currently treated as an error — log noise possible on school holidays / vacation periods (no functional impact) |

> ✅ **Verified working** as of release `v4.2.17`: Pharmacy (live HA query showed sensor state=20 with full attribute payload). Safety Alert (cascading district registration successful).

> 🐛 **Something broke after a site change?** Open a [GitHub issue](https://github.com/redchupa/kr_component_kit/issues) and a fix PR is usually quick.

---

## 🐛 Troubleshooting

### API key auth failures
- After applying, expect **1–2 hours** of activation lag (especially agency-issued keys)
- Within `data.go.kr`, **each dataset needs its own 활용신청** — a pharmacy-approved key returns 403 against weather warnings
- Disaster Alert needs `safetydata.go.kr` specifically — `data.go.kr` keys do not work
- `401` = wrong key, `403` = right key but no application approval for that dataset
- Hit daily quota? Check My Page traffic stats

### Login failures (KEPCO / Arisu / GasApp)
- Confirm the website itself lets you log in normally
- Accounts with 2FA enabled are not supported
- GasApp tokens expire frequently — re-extract from the app

### Empty data (Safety Alert / Disaster Alert)
- If no recent messages in your area, state shows `없음` ("none") — normal
- Government site maintenance? Wait and it auto-recovers

### Still stuck

1. **Check logs** — Settings → System → Logs → search `kr_component_kit`
2. **Open an issue** — [GitHub Issues](https://github.com/redchupa/kr_component_kit/issues) — include:
   - Which service (e.g., "Pharmacy — Seoul Gangnam-gu")
   - HA version + this integration version
   - Error log (mask any personal info / keys)
   - Steps you've tried

> 💬 Both English and Korean issues welcome — responses in your language.

---

## 📋 Requirements

- **Home Assistant** 2023.1.0 or later
- **Python** 3.11+ (HA's own requirement)
- Internet connection (each service hits its respective API)
- Auto-installed Python packages: `curl_cffi>=0.7.0`, `beautifulsoup4>=4.12.0` (declared in manifest.json)

---

## ⚠️ Disclaimer

- This integration uses **authenticated web scraping or mobile-app internal APIs** rather than official OpenAPIs for KEPCO, Arisu, GasApp, and Safety Alert
- Provider policy changes may break these services without warning
- A few government-site clients use `verify=False` (TLS-verification bypass) to work around the sites' TLS configuration quirks — review the source if this concerns you
- All credentials (IDs, passwords, tokens, API keys) are stored only in Home Assistant's local storage. Nothing is sent externally
- This is an **unofficial third-party integration** — not affiliated with the Korean government or any of the listed agencies. Use at your own risk.

---

## 🤝 Contributing & License

- **License**: [MIT](LICENSE) — free to use, modify, and redistribute
- Issues and PRs welcome: <https://github.com/redchupa/kr_component_kit/issues>
- Suggestions for new Korean services to add are very welcome

---

## ⭐ Star if useful

A single Star ⭐ at the top right goes a long way. More stars → higher chance of HACS Default Repository acceptance → more Korean users can discover this.

[![Star History Chart](https://api.star-history.com/svg?repos=redchupa/kr_component_kit&type=Date)](https://star-history.com/#redchupa/kr_component_kit&Date)

---

## ☕ Donations

If this saved you time, a coffee would be appreciated 🙏

<table>
  <tr>
    <td align="center">
      <b>Toss (Korean)</b><br/>
      <img src="https://raw.githubusercontent.com/redchupa/kr_component_kit/main/images/toss-donation.png" alt="Toss donation QR" width="200"/>
    </td>
    <td align="center">
      <b>PayPal</b><br/>
      <img src="https://raw.githubusercontent.com/redchupa/kr_component_kit/main/images/paypal-donation.png" alt="PayPal donation QR" width="200"/>
    </td>
  </tr>
</table>

---

**Made with ❤️ for Korean Home Assistant users**

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/redchupa/kr_component_kit.svg?style=for-the-badge
[releases]: https://github.com/redchupa/kr_component_kit/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/redchupa/kr_component_kit.svg?style=for-the-badge
[commits]: https://github.com/redchupa/kr_component_kit/commits/main
[license-shield]: https://img.shields.io/github/license/redchupa/kr_component_kit.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/redchupa/kr_component_kit.svg?style=for-the-badge
[stars]: https://github.com/redchupa/kr_component_kit/stargazers
