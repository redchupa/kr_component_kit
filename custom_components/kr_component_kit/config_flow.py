"""Config flow for 한국 컴포넌트 키트."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict, SelectSelector, SelectSelectorConfig, SelectSelectorMode,
)
from .const import *

_LOGGER = logging.getLogger(__name__)


_REGION_GRID = {
"11B10101": (60, 127),  # 서울
"11B20201": (55, 124),  # 인천
"11B20601": (60, 121),  # 수원
"11D10301": (73, 134),  # 춘천
"11D20501": (92, 131),  # 강릉
"11C10301": (69, 106),  # 청주
"11C20401": (67, 100),  # 대전
"11F10201": (58, 74),   # 광주
"11F20501": (63, 89),   # 전주
"11H10701": (89, 90),   # 대구
"11H20201": (98, 76),   # 부산
"11H20301": (102, 84),  # 울산
"11G00201": (52, 38),   # 제주
}

class KRPublicDataConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._bus_stops: list[dict] = []
        self._bus_routes: list[dict] = []
        self._selected_stop: dict = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        return self.async_show_menu(
            step_id="user",
            menu_options=["weather_warning", "transit", "fuel", "school",
                         "disaster", "safety_alert", "kepco", "gasapp", "arisu",
                         "pharmacy", "airkorea", "kma_weather", "earthquake",
                         "seoul_bus", "kakao_bus"],
        )

    # ══════════ 기상특보 ══════════

    async def async_step_weather_warning(self, user_input=None) -> FlowResult:
        from .weather import AREA_CODES
        from .weather.api import validate_kma_api
        errors: dict[str, str] = {}
        area_options = [
            SelectOptionDict(value=code, label=f"{name}")
            for code, name in AREA_CODES.items()
        ]
        if user_input is not None:
            api_key = user_input["api_key"]
            areas = user_input.get("area_codes", [])
            if not isinstance(areas, list):
                areas = [areas]
            if not areas:
                errors["area_codes"] = "no_selection"
            elif await validate_kma_api(api_key, areas[0]):
                await self.async_set_unique_id(
                    f"{ENTRY_WEATHER}_" + "_".join(sorted(areas)))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="기상특보",
                    data={CONF_ENTRY_TYPE: ENTRY_WEATHER,
                          "api_key": api_key, "area_codes": areas})
            else:
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="weather_warning",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("area_codes"): SelectSelector(
                    SelectSelectorConfig(options=area_options, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
            }),
            errors=errors)

    # ══════════ 대중교통 ══════════

    async def async_step_transit(self, user_input=None) -> FlowResult:
        if user_input is not None:
            self._data = {
                CONF_ENTRY_TYPE: ENTRY_TRANSIT,
                "seoul_api_key": user_input.get("seoul_api_key", ""),
                "bus_api_key": user_input.get("bus_api_key", ""),
                "subway_items": [], "bus_stops": [],
            }
            return await self.async_step_transit_add()
        return self.async_show_form(
            step_id="transit",
            data_schema=vol.Schema({
                vol.Optional("seoul_api_key"): str,
                vol.Optional("bus_api_key", description={"suggested_value": "환승경로 조회용 (선택)"}): str,
            }))

    async def async_step_transit_add(self, user_input=None) -> FlowResult:
        return self.async_show_menu(
            step_id="transit_add",
            menu_options=["transit_subway", "transit_bus_search", "transit_done"])

    # ── 지하철 ──
    async def async_step_transit_subway(self, user_input=None) -> FlowResult:
        from .transit import DIRECTIONS, SUBWAY_LINES
        if user_input is not None:
            self._data["subway_items"].append({
                "station": user_input["station"].strip(),
                "direction": user_input["direction"],
                "line_id": user_input.get("line_id", ""),
            })
            return await self.async_step_transit_add()
        dir_opts = {d: d for d in DIRECTIONS}
        line_opts = {"": "전체 (필터 없음)"}
        line_opts.update(SUBWAY_LINES)
        return self.async_show_form(
            step_id="transit_subway",
            data_schema=vol.Schema({
                vol.Required("station"): str,
                vol.Required("direction", default="상행"): vol.In(dir_opts),
                vol.Optional("line_id", default=""): vol.In(line_opts),
            }))

    # ── 버스: 정류장 ID 입력 (KakaoMap) ──
    async def async_step_transit_bus_search(self, user_input=None) -> FlowResult:
        import homeassistant.helpers.config_validation as cv
        errors: dict[str, str] = {}
        if user_input is not None:
            stop_id = user_input["kakao_stop_id"].strip()
            from .transit.bus_api import fetch_stop_data, build_bus_labels
            try:
                session = async_get_clientsession(self.hass)
                data = await fetch_stop_data(session, stop_id)
                stop_name = data.get("name", stop_id)
                bus_labels = build_bus_labels(data)
                if not bus_labels:
                    errors["kakao_stop_id"] = "no_stops_found"
                else:
                    self._bus_stop_id = stop_id
                    self._bus_stop_name = stop_name
                    self._bus_labels = bus_labels
                    return await self.async_step_transit_bus_select()
            except Exception as e:
                _LOGGER.error("KakaoMap bus stop error: %s", e)
                errors["kakao_stop_id"] = "cannot_connect"
        return self.async_show_form(
            step_id="transit_bus_search",
            data_schema=vol.Schema({
                vol.Required("kakao_stop_id"): str,
            }),
            errors=errors,
            description_placeholders={
                "tip": "카카오맵에서 정류장 검색 후 URL의 busstopid 값을 입력하세요"
            })

    # ── 버스: 노선 복수 선택 ──
    async def async_step_transit_bus_select(self, user_input=None) -> FlowResult:
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            selected = user_input.get("buses", [])
            self._data.setdefault("bus_stops", []).append({
                "stop_id": self._bus_stop_id,
                "stop_name": self._bus_stop_name,
                "buses": selected,
            })
            return await self.async_step_transit_add()
        return self.async_show_form(
            step_id="transit_bus_select",
            data_schema=vol.Schema({
                vol.Required("buses", default=list(self._bus_labels.keys())):
                    cv.multi_select(self._bus_labels),
            }))

    # ── 대중교통 완료 ──
    async def async_step_transit_done(self, user_input=None) -> FlowResult:
        await self.async_set_unique_id(ENTRY_TRANSIT)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="대중교통", data=self._data)

    # ══════════ 유가정보 ══════════

    async def async_step_fuel(self, user_input=None) -> FlowResult:
        from .fuel import SIDO_CODES, FUEL_TYPES
        from .fuel.api import validate_opinet
        errors: dict[str, str] = {}

        sido_options = [
            SelectOptionDict(value=k, label=v) for k, v in SIDO_CODES.items()
        ]
        fuel_options = [
            SelectOptionDict(value=k, label=v) for k, v in FUEL_TYPES.items()
        ]

        if user_input is not None:
            api_key = user_input["api_key"]
            sidos = user_input.get("sido_codes", [])
            fuels = user_input.get("fuel_codes", [])
            if not isinstance(sidos, list):
                sidos = [sidos]
            if not isinstance(fuels, list):
                fuels = [fuels]
            if not sidos or not fuels:
                errors["base"] = "no_selection"
            elif await validate_opinet(api_key):
                # Build all combinations
                configs = []
                for s in sidos:
                    for f in fuels:
                        configs.append({"sido_code": s, "fuel_code": f})
                await self.async_set_unique_id(
                    f"{ENTRY_FUEL}_" + "_".join(sorted(sidos)) + "__" + "_".join(sorted(fuels)))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="유가정보",
                    data={CONF_ENTRY_TYPE: ENTRY_FUEL,
                          "api_key": api_key, "configs": configs})
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="fuel",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("sido_codes"): SelectSelector(
                    SelectSelectorConfig(options=sido_options, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
                vol.Required("fuel_codes"): SelectSelector(
                    SelectSelectorConfig(options=fuel_options, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
            }),
            errors=errors)

    # ══════════ 학교정보 ══════════

    async def async_step_school(self, user_input=None) -> FlowResult:
        from .school import SCHOOL_LEVELS
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input["api_key"]
            self._data = {CONF_ENTRY_TYPE: ENTRY_SCHOOL,
                          "api_key": api_key,
                          "school_level": user_input["school_level"]}
            try:
                session = async_get_clientsession(self.hass)
                from .school.api import NeisApiClient
                c = NeisApiClient(session, api_key)
                await c.search_school("서울")
            except Exception:
                errors["api_key"] = "invalid_api_key"
            if not errors:
                return await self.async_step_school_search()
        return self.async_show_form(
            step_id="school",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("school_level", default="elementary"): vol.In(SCHOOL_LEVELS),
            }),
            errors=errors)

    async def async_step_school_search(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            from .school.api import NeisApiClient
            from .school.parser import parse_school_info
            c = NeisApiClient(session, self._data["api_key"])
            if "school_search" in user_input:
                schools = await c.search_school(user_input["school_search"])
                if not schools:
                    errors["school_search"] = "no_schools_found"
                else:
                    opts = {
                        f"{s['ATPT_OFCDC_SC_CODE']}_{s['SD_SCHUL_CODE']}":
                        f"{s['SCHUL_NM']} ({s.get('ORG_RDNMA', '')})"
                        for s in schools[:10]}
                    return self.async_show_form(step_id="school_search",
                        data_schema=vol.Schema({vol.Required("selected_school"): vol.In(opts)}))
            elif "selected_school" in user_input:
                rc, sc = user_input["selected_school"].split("_")
                info = await c.get_school_info(rc, sc)
                if info:
                    self._data.update(parse_school_info(info))
                    return await self.async_step_school_class()
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="school_search",
            data_schema=vol.Schema({vol.Required("school_search"): str}),
            errors=errors)

    async def async_step_school_class(self, user_input=None) -> FlowResult:
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            # Parse "G-C" format selections into list
            selected = user_input.get("grade_classes", [])
            self._data["grade_classes"] = selected
            # For backward compat, set grade to first selection's grade
            if selected:
                g, cl = selected[0].split("-")
                self._data["grade"] = int(g)
                self._data["classes"] = [s.split("-")[1] for s in selected]
                self._data["class"] = selected[0].split("-")[1]
            return await self.async_step_school_periods()
        max_g = 6 if self._data["school_level"] == "elementary" else 3
        # Build "학년-반" combo options
        combo_opts = {}
        for g in range(1, max_g + 1):
            for cl in range(1, 21):
                key = f"{g}-{cl}"
                combo_opts[key] = f"{g}학년 {cl}반"
        return self.async_show_form(step_id="school_class", data_schema=vol.Schema({
            vol.Required("grade_classes"): cv.multi_select(combo_opts),
        }))

    async def async_step_school_periods(self, user_input=None) -> FlowResult:
        defaults = {1:"09:00-09:50",2:"10:00-10:50",3:"11:00-11:50",
                     4:"12:00-12:50",5:"13:40-14:30",6:"14:40-15:30",7:"15:40-16:30"}
        if user_input is not None:
            self._data.update(user_input)
            title = "학교정보"
            # School entry uniquely identified by school code + grade-classes.
            classes = "_".join(self._data.get("grade_classes", []))
            await self.async_set_unique_id(
                f"{ENTRY_SCHOOL}_{self._data.get('atpt_code', '')}_"
                f"{self._data.get('school_code', '')}_{classes}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=title, data=self._data)
        schema: dict = {vol.Required("period_1", default=defaults[1]): str}
        for i in range(2, 8):
            schema[vol.Optional(f"period_{i}", default=defaults.get(i, ""))] = str
        schema[vol.Optional("lunch_start", default="12:50")] = str
        schema[vol.Optional("lunch_end", default="13:40")] = str
        return self.async_show_form(step_id="school_periods",
                                    data_schema=vol.Schema(schema))

    # ══════════ 재난정보 ══════════

    async def async_step_disaster(self, user_input=None) -> FlowResult:
        from .disaster.api import validate_disaster_api
        from .pharmacy.regions import PHARMACY_REGIONS
        errors: dict[str, str] = {}
        region_opts = [SelectOptionDict(value="", label="전체 (필터 없음)")]
        for name in ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                      "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]:
            region_opts.append(SelectOptionDict(value=name, label=name))
        # 시군구 dropdown — flat list of all 시군구 names across the country.
        # Replaces the prior free-text input which silently filtered out all
        # alerts on a typo. User can also leave it blank to keep the 시도-only
        # filter, or pick any specific 시군구 to narrow further.
        sgg_opts = [SelectOptionDict(value="", label="시군구 미지정")]
        seen: set[str] = set()
        for sgg_list in PHARMACY_REGIONS.values():
            for sgg in sgg_list:
                if sgg not in seen:
                    seen.add(sgg)
                    sgg_opts.append(SelectOptionDict(value=sgg, label=sgg))
        if user_input is not None:
            api_key = user_input["api_key"]
            if await validate_disaster_api(api_key):
                region = user_input.get("region_filter", "")
                sub = user_input.get("sub_region", "").strip()
                if sub:
                    region = sub  # 세부 지역이 있으면 그것을 사용
                title = f"재난정보 - {region}" if region else "재난정보"
                await self.async_set_unique_id(f"{ENTRY_DISASTER}_{region or 'all'}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=title,
                    data={CONF_ENTRY_TYPE: ENTRY_DISASTER,
                          "api_key": api_key,
                          "region_filter": region})
            else:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="disaster",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Optional("region_filter", default=""): SelectSelector(
                    SelectSelectorConfig(options=region_opts,
                                         mode=SelectSelectorMode.DROPDOWN)),
                vol.Optional("sub_region", default=""): SelectSelector(
                    SelectSelectorConfig(options=sgg_opts,
                                         mode=SelectSelectorMode.DROPDOWN)),
            }),
            errors=errors)

    # ══════════ 안전알림 ══════════

    async def async_step_safety_alert(self, user_input=None) -> FlowResult:
        """Step 1/3 — 시도 선택.

        Cascading 시도 → 시군구 → 읍면동 dropdown via safekorea.go.kr region API.
        Restores the pre-coordinator-migration flow that allowed per-동 alerts
        (e.g. "경기도 시흥시 은행동").
        """
        from .safety_alert.region_api import SafetyAlertRegionApiClient
        errors: dict[str, str] = {}
        client = SafetyAlertRegionApiClient()
        sido_list = await client.async_get_sido_list()
        sido_opts = [SelectOptionDict(value=s["code"], label=s["name"])
                     for s in sido_list]
        if user_input is not None:
            sido_code = user_input["sido_code"]
            sido_name = next((s["name"] for s in sido_list
                              if s["code"] == sido_code), sido_code)
            self._sa_sido_code = sido_code
            self._sa_sido_name = sido_name
            return await self.async_step_safety_alert_sgg()
        return self.async_show_form(step_id="safety_alert", data_schema=vol.Schema({
            vol.Required("sido_code"): SelectSelector(
                SelectSelectorConfig(options=sido_opts,
                                     mode=SelectSelectorMode.DROPDOWN)),
        }), errors=errors)

    async def async_step_safety_alert_sgg(self, user_input=None) -> FlowResult:
        """Step 2/3 — 시군구 선택 (또는 시도 전체)."""
        from .safety_alert.region_api import SafetyAlertRegionApiClient
        errors: dict[str, str] = {}
        client = SafetyAlertRegionApiClient()
        sgg_list = await client.async_get_sgg_list(self._sa_sido_code) or []
        sgg_opts = [SelectOptionDict(value="", label=f"{self._sa_sido_name} 전체 (시군구 미지정)")]
        sgg_opts.extend(SelectOptionDict(value=s["code"], label=s["name"])
                        for s in sgg_list)
        if user_input is not None:
            sgg_code = user_input.get("sgg_code", "")
            if not sgg_code:
                # 시군구 미지정 — 시도 단위로 등록 종료
                return await self._finish_safety_alert(sgg_code="", emd_code="")
            sgg_name = next((s["name"] for s in sgg_list
                             if s["code"] == sgg_code), sgg_code)
            self._sa_sgg_code = sgg_code
            self._sa_sgg_name = sgg_name
            return await self.async_step_safety_alert_emd()
        return self.async_show_form(step_id="safety_alert_sgg", data_schema=vol.Schema({
            vol.Optional("sgg_code", default=""): SelectSelector(
                SelectSelectorConfig(options=sgg_opts,
                                     mode=SelectSelectorMode.DROPDOWN)),
        }), errors=errors)

    async def async_step_safety_alert_emd(self, user_input=None) -> FlowResult:
        """Step 3/3 — 읍면동 선택 (옵션, 미지정 가능)."""
        from .safety_alert.region_api import SafetyAlertRegionApiClient
        errors: dict[str, str] = {}
        client = SafetyAlertRegionApiClient()
        emd_list = await client.async_get_emd_list(
            self._sa_sido_code, self._sa_sgg_code) or []
        emd_opts = [SelectOptionDict(value="", label=f"{self._sa_sgg_name} 전체 (읍면동 미지정)")]
        emd_opts.extend(SelectOptionDict(value=e["code"], label=e["name"])
                        for e in emd_list)
        if user_input is not None:
            return await self._finish_safety_alert(
                sgg_code=self._sa_sgg_code,
                emd_code=user_input.get("emd_code", ""))
        return self.async_show_form(step_id="safety_alert_emd", data_schema=vol.Schema({
            vol.Optional("emd_code", default=""): SelectSelector(
                SelectSelectorConfig(options=emd_opts,
                                     mode=SelectSelectorMode.DROPDOWN)),
        }), errors=errors)

    async def _finish_safety_alert(self, sgg_code: str, emd_code: str) -> FlowResult:
        """Build the region entry and create the config entry."""
        # Compose a friendly title — e.g. "안전알림 (경기도 시흥시 은행동)"
        parts = [self._sa_sido_name]
        if sgg_code:
            parts.append(self._sa_sgg_name)
        if emd_code:
            # emd name is whatever the user just selected; we don't have it
            # cached, but the title is cosmetic — sgg-level granularity is
            # enough for the device label.
            pass
        title_region = " ".join(parts)
        region_item = {
            "code": self._sa_sido_code,
            "name": title_region,
            "code2": sgg_code or None,
            "code3": emd_code or None,
        }
        unique_parts = [self._sa_sido_code, sgg_code or "x", emd_code or "x"]
        await self.async_set_unique_id(
            f"{ENTRY_SAFETY_ALERT}_" + "_".join(unique_parts))
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"안전알림 ({title_region})",
            data={CONF_ENTRY_TYPE: ENTRY_SAFETY_ALERT,
                  "regions": [region_item]})

    # ══════════ 한전 (KEPCO) ══════════

    async def async_step_kepco(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            from .kepco.api import KepcoApiClient
            from .kepco.coordinator import KepcoCoordinator
            username = user_input["username"]
            password = user_input["password"]
            try:
                # Reuse the coordinator's session-init logic for the probe.
                probe = KepcoCoordinator(self.hass, username, password)
                logged_in = await probe.async_login()
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("KEPCO validation error: %s", e)
                errors["base"] = "cannot_connect"
            else:
                if not logged_in:
                    errors["base"] = "invalid_auth"
                else:
                    await self.async_set_unique_id(f"{ENTRY_KEPCO}_{username}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"한전 ({username})",
                        data={CONF_ENTRY_TYPE: ENTRY_KEPCO,
                              "username": username,
                              "password": password})
        return self.async_show_form(step_id="kepco", data_schema=vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        }), errors=errors)

    # ══════════ 가스앱 ══════════

    async def async_step_gasapp(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            from .gasapp.api import GasAppApiClient
            from .gasapp.exceptions import GasAppAuthError, GasAppConnectionError
            session = async_get_clientsession(self.hass)
            client = GasAppApiClient(session)
            client.set_credentials(user_input["token"],
                                    user_input["member_id"],
                                    user_input["contract_num"])
            try:
                ok = await client.async_validate_credentials()
            except GasAppAuthError:
                errors["base"] = "invalid_auth"
            except GasAppConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("GasApp validation error: %s", e)
                errors["base"] = "cannot_connect"
            else:
                if not ok:
                    errors["base"] = "invalid_auth"
                else:
                    await self.async_set_unique_id(
                        f"{ENTRY_GASAPP}_{user_input['contract_num']}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"가스앱 ({user_input['contract_num']})",
                        data={CONF_ENTRY_TYPE: ENTRY_GASAPP,
                              "token": user_input["token"],
                              "member_id": user_input["member_id"],
                              "contract_num": user_input["contract_num"]})
        return self.async_show_form(step_id="gasapp", data_schema=vol.Schema({
            vol.Required("token"): str,
            vol.Required("member_id"): str,
            vol.Required("contract_num"): str,
        }), errors=errors)

    # ══════════ 아리수 (서울 상수도) ══════════

    async def async_step_arisu(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            from .arisu.api import ArisuApiClient
            from .arisu.exceptions import ArisuConnectionError, ArisuDataError
            session = async_get_clientsession(self.hass)
            client = ArisuApiClient(session)
            try:
                data = await client.async_get_water_bill_data(
                    user_input["customer_number"], user_input["customer_name"])
            except ArisuConnectionError:
                errors["base"] = "cannot_connect"
            except ArisuDataError:
                errors["base"] = "invalid_auth"
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Arisu validation error: %s", e)
                errors["base"] = "cannot_connect"
            else:
                if not data.get("success", False):
                    # No bill data for any of the recent months -> typically
                    # a wrong customer number/name combination.
                    errors["base"] = "invalid_auth"
                else:
                    await self.async_set_unique_id(
                        f"{ENTRY_ARISU}_{user_input['customer_number']}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"아리수 ({user_input['customer_number']})",
                        data={CONF_ENTRY_TYPE: ENTRY_ARISU,
                              "customer_number": user_input["customer_number"],
                              "customer_name": user_input["customer_name"]})
        return self.async_show_form(step_id="arisu", data_schema=vol.Schema({
            vol.Required("customer_number"): str,
            vol.Required("customer_name"): str,
        }), errors=errors)

    # ══════════ 약국 ══════════

    async def async_step_pharmacy(self, user_input=None) -> FlowResult:
        """Step 1: 서비스 키 + 시도 선택 (서비스 키 즉시 검증)."""
        from .pharmacy.api import PharmacyApiError, fetch_pharmacies
        from .pharmacy.regions import SIDO_LIST
        errors: dict[str, str] = {}
        sido_opts = {name: name for name in SIDO_LIST}
        if user_input is not None:
            api_key = user_input["api_key"].strip()
            q0 = user_input["q0"]
            try:
                await fetch_pharmacies(api_key, q0, "", num=1)
            except PharmacyApiError as e:
                _LOGGER.warning("Pharmacy validation failed: %s", e)
                errors["base"] = "invalid_api_key"
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Pharmacy validation error: %s", e)
                errors["base"] = "cannot_connect"
            else:
                self._data["pharmacy_api_key"] = api_key
                self._data["pharmacy_q0"] = q0
                return await self.async_step_pharmacy_sgg()
        return self.async_show_form(
            step_id="pharmacy",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("q0", default="서울특별시"): vol.In(sido_opts),
            }),
            errors=errors,
            description_placeholders={
                "api_key_desc": "공공데이터포털(data.go.kr)에서 발급받은 서비스 키",
                "q0_desc": "시도를 선택하세요",
            },
        )

    async def async_step_pharmacy_sgg(self, user_input=None) -> FlowResult:
        """Step 2: 선택된 시도의 시군구 dropdown (선택 사항)."""
        from .pharmacy.regions import get_sgg_list
        q0 = self._data.get("pharmacy_q0", "")
        sgg_list = get_sgg_list(q0)
        # "" 키 = 시도 전체 검색 (시군구 미지정)
        sgg_opts: dict[str, str] = {"": f"{q0} 전체 (시군구 미지정)"}
        for name in sgg_list:
            sgg_opts[name] = name
        if user_input is not None:
            q1 = user_input.get("q1", "")
            await self.async_set_unique_id(
                f"{ENTRY_PHARMACY}_{q0}_{q1 or 'all'}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"약국 정보 ({q0}{f' {q1}' if q1 else ''})",
                data={
                    CONF_ENTRY_TYPE: ENTRY_PHARMACY,
                    "api_key": self._data["pharmacy_api_key"],
                    "q0": q0,
                    "q1": q1,
                },
            )
        return self.async_show_form(
            step_id="pharmacy_sgg",
            data_schema=vol.Schema({
                vol.Optional("q1", default=""): vol.In(sgg_opts),
            }),
            description_placeholders={
                "q1_desc": f"{q0}의 시군구를 선택하세요 (미지정 시 시도 전체)",
            },
        )




# 기상청 예보구역 격자 좌표

    # ══════════ 에어코리아 ══════════
    async def async_step_airkorea(self, user_input=None) -> FlowResult:
        """Step 1: API key + 광역시도 선택."""
        from .airkorea import STATIONS_BY_SIDO
        air_sido = list(STATIONS_BY_SIDO.keys())
        errors: dict[str, str] = {}
        if user_input is not None:
            self._data = {CONF_ENTRY_TYPE: ENTRY_AIRKOREA,
                          "api_key": user_input["api_key"],
                          "living_api_key": user_input.get("living_api_key", "")}
            self._air_sido = user_input["sido"]
            return await self.async_step_airkorea_select()
        sido_opts = [SelectOptionDict(value=k, label=k) for k in air_sido]
        return self.async_show_form(step_id="airkorea", data_schema=vol.Schema({
            vol.Required("api_key"): str,
            vol.Optional("living_api_key", default=""): str,
            vol.Required("sido", default="서울"): SelectSelector(
                SelectSelectorConfig(options=sido_opts, mode=SelectSelectorMode.DROPDOWN)),
        }), errors=errors)

    async def async_step_airkorea_select(self, user_input=None) -> FlowResult:
        """Step 2: 측정소(시군구) 복수 선택."""
        import homeassistant.helpers.config_validation as cv
        from .airkorea import STATIONS_BY_SIDO
        if user_input is not None:
            selected = user_input.get("stations", [])
            self._data["stations"] = [{"stationName": s} for s in selected]
            self._data["sido"] = self._air_sido
            await self.async_set_unique_id(f"{ENTRY_AIRKOREA}_{self._air_sido}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="에어코리아", data=self._data)
        station_list = STATIONS_BY_SIDO.get(self._air_sido, [])
        labels = {s: s for s in station_list}
        return self.async_show_form(step_id="airkorea_select", data_schema=vol.Schema({
            vol.Required("stations", default=station_list[:3]): cv.multi_select(labels),
        }))

    # ══════════ 기상청 날씨예보 ══════════
    async def async_step_kma_weather(self, user_input=None) -> FlowResult:
        """Step 1: API key + 광역시도 선택."""
        from .kma_weather import SIDO_LIST
        from .kma_weather.api import KMAApiError, fetch_vilage_forecast
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input["api_key"]
            session = async_get_clientsession(self.hass)
            try:
                # Probe with Seoul (nx=60, ny=127) — known stable grid point.
                await fetch_vilage_forecast(session, api_key, 60, 127)
            except KMAApiError as e:
                _LOGGER.warning("KMA validation failed: %s", e)
                errors["base"] = "invalid_api_key"
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("KMA validation error: %s", e)
                errors["base"] = "cannot_connect"
            else:
                self._data = {CONF_ENTRY_TYPE: ENTRY_KMA_WEATHER,
                              "api_key": api_key}
                self._kma_sido = user_input["sido"]
                return await self.async_step_kma_weather_sgg()
        sido_opts = [SelectOptionDict(value=k, label=k) for k in SIDO_LIST.keys()]
        return self.async_show_form(step_id="kma_weather", data_schema=vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("sido_code"): SelectSelector(
                SelectSelectorConfig(options=sido_opts,
                                     mode=SelectSelectorMode.DROPDOWN)),
        }), errors=errors)

    async def async_step_kma_weather_sgg(self, user_input=None) -> FlowResult:
        """Step 2: 기초자치단체 + O3/UV 측정소 선택."""
        import homeassistant.helpers.config_validation as cv
        from .kma_weather import SIDO_LIST
        from .airkorea import STATIONS_BY_SIDO, SIDO_AREA_CODE
        sgg_map = SIDO_LIST.get(self._kma_sido, {})
        if user_input is not None:
            selected = user_input.get("regions", [])
            regions = [{"name": r,
                        "nx": sgg_map[r][0], "ny": sgg_map[r][1]}
                       for r in selected if r in sgg_map]
            self._data["regions"] = regions
            self._data["air_station"] = user_input.get("air_station", "")
            self._data["area_no"] = SIDO_AREA_CODE.get(self._kma_sido, "")
            self._data["sido"] = self._kma_sido
            await self.async_set_unique_id(
                f"{ENTRY_KMA_WEATHER}_{self._kma_sido}_"
                + "_".join(sorted(r["name"] for r in regions)))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="기상청 날씨예보", data=self._data)
        labels = {k: k for k in sgg_map.keys()}
        air_stations = STATIONS_BY_SIDO.get(self._kma_sido, [])
        air_opts = {"": "사용 안 함 (날씨만)"}
        air_opts.update({s: f"{s} (O₃/UV 포함)" for s in air_stations[:30]})
        return self.async_show_form(step_id="kma_weather_sgg", data_schema=vol.Schema({
            vol.Required("regions"): cv.multi_select(labels),
            vol.Optional("air_station", default=""): vol.In(air_opts),
        }))

    # ══════════ 지진 정보 ══════════
    async def async_step_earthquake(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(ENTRY_EARTHQUAKE)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="지진 정보",
                data={CONF_ENTRY_TYPE: ENTRY_EARTHQUAKE,
                      "api_key": user_input["api_key"],
                      "home_latitude": user_input.get("latitude", 37.5665),
                      "home_longitude": user_input.get("longitude", 126.978),
                      "radius_km": user_input.get("radius_km", 200),
                      "min_magnitude": user_input.get("min_magnitude", 3.0)})
        return self.async_show_form(step_id="earthquake", data_schema=vol.Schema({
            vol.Required("api_key"): str,
            vol.Optional("latitude", default=37.5665): vol.Coerce(float),
            vol.Optional("longitude", default=126.978): vol.Coerce(float),
            vol.Optional("radius_km", default=200): vol.Coerce(int),
            vol.Optional("min_magnitude", default=3.0): vol.Coerce(float),
        }), errors=errors)

    # ══════════ 서울 버스 ══════════
    async def async_step_seoul_bus(self, user_input=None) -> FlowResult:
        """Step 1: API key validation, then loop into station-add flow."""
        from .seoul_bus.api import validate_api_key
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input["api_key"].strip()
            session = async_get_clientsession(self.hass)
            err = await validate_api_key(session, api_key)
            if err is None:
                self._data = {CONF_ENTRY_TYPE: ENTRY_SEOUL_BUS,
                              "api_key": api_key,
                              "stations": []}
                return await self.async_step_seoul_bus_add()
            # `invalid_api_key` is field-level; `cannot_connect` is form-level
            # so the message lands above the form, not under the key field.
            errors["api_key" if err == "invalid_api_key" else "base"] = err
        return self.async_show_form(
            step_id="seoul_bus",
            data_schema=vol.Schema({vol.Required("api_key"): str}),
            errors=errors,
        )

    async def async_step_seoul_bus_add(self, user_input=None) -> FlowResult:
        """Ask for an ARS-ID, probe it, then go to route selection."""
        from .seoul_bus.api import SeoulBusApiError, build_route_labels, fetch_station
        errors: dict[str, str] = {}
        if user_input is not None:
            ars_id = user_input["ars_id"].strip()
            session = async_get_clientsession(self.hass)
            try:
                items = await fetch_station(
                    session, self._data["api_key"], ars_id)
            except SeoulBusApiError as e:
                _LOGGER.warning("Seoul Bus station probe failed: %s", e)
                errors["ars_id"] = "cannot_connect"
                items = []
            if not errors:
                if not items:
                    errors["ars_id"] = "no_stops_found"
                else:
                    self._sb_ars_id = ars_id
                    # Pick the first non-empty `stNm` across items rather than
                    # blindly trusting items[0] — defensive against carriers
                    # occasionally returning the station name on later rows.
                    api_station_name = next(
                        (it.get("stNm") for it in items if it.get("stNm")),
                        "",
                    )
                    self._sb_station_name = (
                        user_input.get("station_name", "").strip()
                        or api_station_name
                        or f"정류장 {ars_id}"
                    )
                    self._sb_route_labels = build_route_labels(items)
                    return await self.async_step_seoul_bus_routes()
        return self.async_show_form(
            step_id="seoul_bus_add",
            data_schema=vol.Schema({
                vol.Required("ars_id"): str,
                vol.Optional("station_name", default=""): str,
            }),
            errors=errors,
        )

    async def async_step_seoul_bus_routes(self, user_input=None) -> FlowResult:
        """Pick which routes at this station to expose as sensors."""
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            self._data["stations"].append({
                "ars_id": self._sb_ars_id,
                "station_name": self._sb_station_name,
                "routes": user_input.get("routes", []),
            })
            return await self.async_step_seoul_bus_menu()
        labels = self._sb_route_labels
        return self.async_show_form(
            step_id="seoul_bus_routes",
            data_schema=vol.Schema({
                vol.Required("routes", default=list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_seoul_bus_menu(self, user_input=None) -> FlowResult:
        """After adding a station, offer another or finish."""
        return self.async_show_menu(
            step_id="seoul_bus_menu",
            menu_options=["seoul_bus_add", "seoul_bus_done"],
        )

    async def async_step_seoul_bus_done(self, user_input=None) -> FlowResult:
        ids = "_".join(sorted(s["ars_id"] for s in self._data["stations"]))
        await self.async_set_unique_id(f"{ENTRY_SEOUL_BUS}_{ids}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="서울버스", data=self._data)

    # ══════════ 카카오 버스 ══════════
    async def async_step_kakao_bus(self, user_input=None) -> FlowResult:
        """Step 1 — enter a bus stop name to search."""
        from .kakao_bus.api import KakaoBusApiError, search_stops
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input["stop_name"].strip()
            session = async_get_clientsession(self.hass)
            try:
                stops = await search_stops(session, name)
            except KakaoBusApiError as e:
                _LOGGER.warning("KakaoMap search failed: %s", e)
                errors["base"] = "cannot_connect"
                stops = {}
            if not errors:
                if not stops:
                    errors["stop_name"] = "no_stops_found"
                else:
                    self._data = {CONF_ENTRY_TYPE: ENTRY_KAKAO_BUS, "stops": []}
                    self._kbus_results = stops
                    return await self.async_step_kakao_bus_select_stop()
        return self.async_show_form(
            step_id="kakao_bus",
            data_schema=vol.Schema({vol.Required("stop_name"): str}),
            errors=errors,
        )

    async def async_step_kakao_bus_search(self, user_input=None) -> FlowResult:
        """Repeat search (used when adding more stops to an existing entry)."""
        from .kakao_bus.api import KakaoBusApiError, search_stops
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input["stop_name"].strip()
            session = async_get_clientsession(self.hass)
            try:
                stops = await search_stops(session, name)
            except KakaoBusApiError as e:
                _LOGGER.warning("KakaoMap search failed: %s", e)
                errors["base"] = "cannot_connect"
                stops = {}
            if not errors:
                if not stops:
                    errors["stop_name"] = "no_stops_found"
                else:
                    self._kbus_results = stops
                    return await self.async_step_kakao_bus_select_stop()
        return self.async_show_form(
            step_id="kakao_bus_search",
            data_schema=vol.Schema({vol.Required("stop_name"): str}),
            errors=errors,
        )

    async def async_step_kakao_bus_select_stop(self, user_input=None) -> FlowResult:
        """Step 2 — pick a stop from the search results, then probe routes."""
        from .kakao_bus.api import KakaoBusApiError, fetch_stop_routes
        errors: dict[str, str] = {}
        if user_input is not None:
            stop_id = user_input["stop_id"]
            stop_info = self._kbus_results.get(stop_id) or {}
            session = async_get_clientsession(self.hass)
            try:
                routes = await fetch_stop_routes(session, stop_id)
            except KakaoBusApiError as e:
                _LOGGER.warning("KakaoMap stop-routes failed: %s", e)
                errors["base"] = "cannot_connect"
                routes = []
            if not errors:
                if not routes:
                    errors["base"] = "no_stops_found"
                else:
                    self._kbus_stop_id = stop_id
                    self._kbus_stop_name = stop_info.get("title") or stop_id
                    self._kbus_routes = routes
                    return await self.async_step_kakao_bus_select_routes()
        opts = {k: v["title"] for k, v in self._kbus_results.items()}
        return self.async_show_form(
            step_id="kakao_bus_select_stop",
            data_schema=vol.Schema({vol.Required("stop_id"): vol.In(opts)}),
            errors=errors,
        )

    async def async_step_kakao_bus_select_routes(
        self, user_input=None) -> FlowResult:
        """Step 3 — pick routes at the chosen stop."""
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            self._data["stops"].append({
                "stop_id": self._kbus_stop_id,
                "stop_name": self._kbus_stop_name,
                "routes": user_input.get("routes", []),
            })
            return await self.async_step_kakao_bus_menu()
        labels = {
            r["number"]: (f"{r['type']} {r['number']}".strip()
                          if r["type"] else r["number"])
            for r in self._kbus_routes
        }
        return self.async_show_form(
            step_id="kakao_bus_select_routes",
            data_schema=vol.Schema({
                vol.Required("routes", default=list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_kakao_bus_menu(self, user_input=None) -> FlowResult:
        return self.async_show_menu(
            step_id="kakao_bus_menu",
            menu_options=["kakao_bus_search", "kakao_bus_done"],
        )

    async def async_step_kakao_bus_done(self, user_input=None) -> FlowResult:
        ids = "_".join(sorted(s["stop_id"] for s in self._data["stops"]))
        await self.async_set_unique_id(f"{ENTRY_KAKAO_BUS}_{ids}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="카카오버스", data=self._data)

        # ══════════ Options Flow =════════

    @staticmethod
    def async_get_options_flow(config_entry):
        return KRPublicDataOptionsFlow(config_entry)


class KRPublicDataOptionsFlow(config_entries.OptionsFlow):
    """Handle options for reconfiguration."""

    def __init__(self, config_entry):
        self._entry = config_entry
        # Working copies used by the menu-driven seoul_bus / kakao_bus
        # option flows. None until first menu visit; persisted to entry.data
        # only when the user picks "Save & Exit".
        self._stations: list[dict] | None = None  # seoul_bus
        self._stops: list[dict] | None = None  # kakao_bus
        self._new_api_key: str | None = None  # seoul_bus
        self._new_scan_interval: int | None = None  # kakao_bus
        # Per-sub-step scratch space
        self._opt_sb_ars_id: str | None = None
        self._opt_sb_station_name: str | None = None
        self._opt_sb_route_labels: dict | None = None
        self._opt_kbus_results: dict | None = None
        self._opt_kbus_stop_id: str | None = None
        self._opt_kbus_stop_name: str | None = None
        self._opt_kbus_routes: list | None = None

    async def async_step_init(self, user_input=None):
        """Entry-point step — bus types branch into a menu, others use schema."""
        etype = self._entry.data.get(CONF_ENTRY_TYPE)

        if etype == ENTRY_SEOUL_BUS:
            if self._stations is None:
                self._stations = [dict(s) for s
                                  in self._entry.data.get("stations", [])]
                self._new_api_key = self._entry.data.get("api_key", "")
            return self.async_show_menu(
                step_id="init",
                menu_options=[
                    "seoul_bus_opt_add",
                    "seoul_bus_opt_remove",
                    "seoul_bus_opt_edit_routes",
                    "seoul_bus_opt_edit_key",
                    "seoul_bus_opt_done",
                ],
            )

        if etype == ENTRY_KAKAO_BUS:
            if self._stops is None:
                self._stops = [dict(s) for s
                               in self._entry.data.get("stops", [])]
                from .kakao_bus import KAKAO_BUS_SCAN_INTERVAL
                self._new_scan_interval = (
                    self._entry.options.get("scan_interval")
                    or self._entry.data.get(
                        "scan_interval", KAKAO_BUS_SCAN_INTERVAL)
                )
            return self.async_show_menu(
                step_id="init",
                menu_options=[
                    "kakao_bus_opt_add",
                    "kakao_bus_opt_remove",
                    "kakao_bus_opt_edit_routes",
                    "kakao_bus_opt_edit_interval",
                    "kakao_bus_opt_done",
                ],
            )

        # Other entry types: classic schema-based flow.
        if user_input is not None:
            new_data = {**self._entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self._entry, data=new_data)
            return self.async_create_entry(title="", data=user_input)

        schema = self._build_schema(etype)
        if schema is None:
            return self.async_abort(reason="no_options")
        return self.async_show_form(step_id="init", data_schema=schema)

    # ─────────────────────────── 서울버스 옵션 ───────────────────────────

    async def async_step_seoul_bus_opt_add(self, user_input=None):
        """Add a new station to the working copy."""
        from .seoul_bus.api import (
            SeoulBusApiError, build_route_labels, fetch_station)
        errors: dict[str, str] = {}
        if user_input is not None:
            ars_id = user_input["ars_id"].strip()
            if any(s["ars_id"] == ars_id for s in self._stations):
                errors["ars_id"] = "already_added"
            else:
                session = async_get_clientsession(self.hass)
                try:
                    items = await fetch_station(
                        session, self._new_api_key, ars_id)
                except SeoulBusApiError as e:
                    _LOGGER.warning("Seoul Bus station probe failed: %s", e)
                    errors["ars_id"] = "cannot_connect"
                    items = []
                if not errors:
                    if not items:
                        errors["ars_id"] = "no_stops_found"
                    else:
                        self._opt_sb_ars_id = ars_id
                        api_name = next(
                            (it.get("stNm") for it in items if it.get("stNm")),
                            "")
                        self._opt_sb_station_name = (
                            user_input.get("station_name", "").strip()
                            or api_name
                            or f"정류장 {ars_id}"
                        )
                        self._opt_sb_route_labels = build_route_labels(items)
                        return await self.async_step_seoul_bus_opt_add_routes()
        return self.async_show_form(
            step_id="seoul_bus_opt_add",
            data_schema=vol.Schema({
                vol.Required("ars_id"): str,
                vol.Optional("station_name", default=""): str,
            }),
            errors=errors,
        )

    async def async_step_seoul_bus_opt_add_routes(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            self._stations.append({
                "ars_id": self._opt_sb_ars_id,
                "station_name": self._opt_sb_station_name,
                "routes": user_input.get("routes", []),
            })
            return await self.async_step_init()
        labels = self._opt_sb_route_labels or {}
        return self.async_show_form(
            step_id="seoul_bus_opt_add_routes",
            data_schema=vol.Schema({
                vol.Required("routes", default=list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_seoul_bus_opt_remove(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        errors: dict[str, str] = {}
        if user_input is not None:
            to_remove = set(user_input.get("ars_ids", []))
            if not to_remove:
                errors["base"] = "no_selection"
            else:
                self._stations = [s for s in self._stations
                                  if s["ars_id"] not in to_remove]
                return await self.async_step_init()
        if not self._stations:
            return await self.async_step_init()
        labels = {
            s["ars_id"]:
                f"{s.get('station_name') or s['ars_id']} ({s['ars_id']})"
            for s in self._stations
        }
        return self.async_show_form(
            step_id="seoul_bus_opt_remove",
            data_schema=vol.Schema({
                vol.Required("ars_ids"): cv.multi_select(labels),
            }),
            errors=errors,
        )

    async def async_step_seoul_bus_opt_edit_routes(self, user_input=None):
        from .seoul_bus.api import (
            SeoulBusApiError, build_route_labels, fetch_station)
        errors: dict[str, str] = {}
        if user_input is not None:
            ars_id = user_input["ars_id"]
            session = async_get_clientsession(self.hass)
            try:
                items = await fetch_station(
                    session, self._new_api_key, ars_id)
            except SeoulBusApiError as e:
                _LOGGER.warning("Seoul Bus station probe failed: %s", e)
                errors["base"] = "cannot_connect"
                items = []
            if not errors:
                if not items:
                    errors["base"] = "no_stops_found"
                else:
                    self._opt_sb_ars_id = ars_id
                    self._opt_sb_route_labels = build_route_labels(items)
                    return await self.async_step_seoul_bus_opt_edit_routes_pick()
        if not self._stations:
            return await self.async_step_init()
        labels = {
            s["ars_id"]: s.get("station_name") or s["ars_id"]
            for s in self._stations
        }
        return self.async_show_form(
            step_id="seoul_bus_opt_edit_routes",
            data_schema=vol.Schema({vol.Required("ars_id"): vol.In(labels)}),
            errors=errors,
        )

    async def async_step_seoul_bus_opt_edit_routes_pick(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            for s in self._stations:
                if s["ars_id"] == self._opt_sb_ars_id:
                    s["routes"] = user_input.get("routes", [])
                    break
            return await self.async_step_init()
        labels = self._opt_sb_route_labels or {}
        current = next(
            (s.get("routes", []) for s in self._stations
             if s["ars_id"] == self._opt_sb_ars_id),
            [])
        return self.async_show_form(
            step_id="seoul_bus_opt_edit_routes_pick",
            data_schema=vol.Schema({
                vol.Required("routes", default=current or list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_seoul_bus_opt_edit_key(self, user_input=None):
        from .seoul_bus.api import validate_api_key
        errors: dict[str, str] = {}
        if user_input is not None:
            new_key = user_input["api_key"].strip()
            session = async_get_clientsession(self.hass)
            err = await validate_api_key(session, new_key)
            if err is None:
                self._new_api_key = new_key
                return await self.async_step_init()
            errors["api_key" if err == "invalid_api_key" else "base"] = err
        return self.async_show_form(
            step_id="seoul_bus_opt_edit_key",
            data_schema=vol.Schema({
                vol.Required("api_key", default=self._new_api_key or ""): str,
            }),
            errors=errors,
        )

    async def async_step_seoul_bus_opt_done(self, user_input=None):
        if not self._stations:
            # Refuse to leave the entry with zero stations — go back to menu.
            return await self.async_step_init()
        new_data = {
            **self._entry.data,
            "api_key": self._new_api_key,
            "stations": self._stations,
        }
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        return self.async_create_entry(title="", data={})

    # ─────────────────────────── 카카오버스 옵션 ──────────────────────────

    async def async_step_kakao_bus_opt_add(self, user_input=None):
        from .kakao_bus.api import KakaoBusApiError, search_stops
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input["stop_name"].strip()
            session = async_get_clientsession(self.hass)
            try:
                stops = await search_stops(session, name)
            except KakaoBusApiError as e:
                _LOGGER.warning("KakaoMap search failed: %s", e)
                errors["base"] = "cannot_connect"
                stops = {}
            if not errors:
                if not stops:
                    errors["stop_name"] = "no_stops_found"
                else:
                    self._opt_kbus_results = stops
                    return await self.async_step_kakao_bus_opt_add_pick()
        return self.async_show_form(
            step_id="kakao_bus_opt_add",
            data_schema=vol.Schema({vol.Required("stop_name"): str}),
            errors=errors,
        )

    async def async_step_kakao_bus_opt_add_pick(self, user_input=None):
        from .kakao_bus.api import KakaoBusApiError, fetch_stop_routes
        errors: dict[str, str] = {}
        if user_input is not None:
            stop_id = user_input["stop_id"]
            if any(s["stop_id"] == stop_id for s in self._stops):
                errors["base"] = "already_added"
            else:
                stop_info = (self._opt_kbus_results or {}).get(stop_id) or {}
                session = async_get_clientsession(self.hass)
                try:
                    routes = await fetch_stop_routes(session, stop_id)
                except KakaoBusApiError as e:
                    _LOGGER.warning("KakaoMap stop-routes failed: %s", e)
                    errors["base"] = "cannot_connect"
                    routes = []
                if not errors:
                    if not routes:
                        errors["base"] = "no_stops_found"
                    else:
                        self._opt_kbus_stop_id = stop_id
                        self._opt_kbus_stop_name = stop_info.get("title") or stop_id
                        self._opt_kbus_routes = routes
                        return await self.async_step_kakao_bus_opt_add_routes()
        opts = {k: v["title"] for k, v in (self._opt_kbus_results or {}).items()}
        return self.async_show_form(
            step_id="kakao_bus_opt_add_pick",
            data_schema=vol.Schema({vol.Required("stop_id"): vol.In(opts)}),
            errors=errors,
        )

    async def async_step_kakao_bus_opt_add_routes(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            self._stops.append({
                "stop_id": self._opt_kbus_stop_id,
                "stop_name": self._opt_kbus_stop_name,
                "routes": user_input.get("routes", []),
            })
            return await self.async_step_init()
        labels = {
            r["number"]: (f"{r['type']} {r['number']}".strip()
                          if r["type"] else r["number"])
            for r in (self._opt_kbus_routes or [])
        }
        return self.async_show_form(
            step_id="kakao_bus_opt_add_routes",
            data_schema=vol.Schema({
                vol.Required("routes", default=list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_kakao_bus_opt_remove(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        errors: dict[str, str] = {}
        if user_input is not None:
            to_remove = set(user_input.get("stop_ids", []))
            if not to_remove:
                errors["base"] = "no_selection"
            else:
                self._stops = [s for s in self._stops
                               if s["stop_id"] not in to_remove]
                return await self.async_step_init()
        if not self._stops:
            return await self.async_step_init()
        labels = {s["stop_id"]: s.get("stop_name") or s["stop_id"]
                  for s in self._stops}
        return self.async_show_form(
            step_id="kakao_bus_opt_remove",
            data_schema=vol.Schema({
                vol.Required("stop_ids"): cv.multi_select(labels),
            }),
            errors=errors,
        )

    async def async_step_kakao_bus_opt_edit_routes(self, user_input=None):
        from .kakao_bus.api import KakaoBusApiError, fetch_stop_routes
        errors: dict[str, str] = {}
        if user_input is not None:
            stop_id = user_input["stop_id"]
            session = async_get_clientsession(self.hass)
            try:
                routes = await fetch_stop_routes(session, stop_id)
            except KakaoBusApiError as e:
                _LOGGER.warning("KakaoMap stop-routes failed: %s", e)
                errors["base"] = "cannot_connect"
                routes = []
            if not errors:
                if not routes:
                    errors["base"] = "no_stops_found"
                else:
                    self._opt_kbus_stop_id = stop_id
                    self._opt_kbus_routes = routes
                    return await self.async_step_kakao_bus_opt_edit_routes_pick()
        if not self._stops:
            return await self.async_step_init()
        labels = {s["stop_id"]: s.get("stop_name") or s["stop_id"]
                  for s in self._stops}
        return self.async_show_form(
            step_id="kakao_bus_opt_edit_routes",
            data_schema=vol.Schema({vol.Required("stop_id"): vol.In(labels)}),
            errors=errors,
        )

    async def async_step_kakao_bus_opt_edit_routes_pick(self, user_input=None):
        import homeassistant.helpers.config_validation as cv
        if user_input is not None:
            for s in self._stops:
                if s["stop_id"] == self._opt_kbus_stop_id:
                    s["routes"] = user_input.get("routes", [])
                    break
            return await self.async_step_init()
        labels = {
            r["number"]: (f"{r['type']} {r['number']}".strip()
                          if r["type"] else r["number"])
            for r in (self._opt_kbus_routes or [])
        }
        current = next(
            (s.get("routes", []) for s in self._stops
             if s["stop_id"] == self._opt_kbus_stop_id),
            [])
        return self.async_show_form(
            step_id="kakao_bus_opt_edit_routes_pick",
            data_schema=vol.Schema({
                vol.Required("routes", default=current or list(labels.keys())):
                    cv.multi_select(labels),
            }),
        )

    async def async_step_kakao_bus_opt_edit_interval(self, user_input=None):
        from .kakao_bus import KAKAO_BUS_SCAN_INTERVAL
        if user_input is not None:
            self._new_scan_interval = user_input["scan_interval"]
            return await self.async_step_init()
        return self.async_show_form(
            step_id="kakao_bus_opt_edit_interval",
            data_schema=vol.Schema({
                vol.Required("scan_interval",
                             default=self._new_scan_interval
                                     or KAKAO_BUS_SCAN_INTERVAL):
                    vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }),
        )

    async def async_step_kakao_bus_opt_done(self, user_input=None):
        if not self._stops:
            return await self.async_step_init()
        new_data = {**self._entry.data, "stops": self._stops}
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        return self.async_create_entry(
            title="",
            data={"scan_interval": self._new_scan_interval}
                  if self._new_scan_interval else {},
        )

    def _build_schema(self, etype):
        d = self._entry.data

        if etype == ENTRY_WEATHER:
            from .weather import AREA_CODES
            area_options = [SelectOptionDict(value=c, label=n) for c, n in AREA_CODES.items()]
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
                vol.Required("area_codes", default=d.get("area_codes", [])): SelectSelector(
                    SelectSelectorConfig(options=area_options, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
            })

        elif etype == ENTRY_TRANSIT:
            return vol.Schema({
                vol.Optional("seoul_api_key", default=d.get("seoul_api_key", "")): str,
                vol.Optional("bus_api_key", default=d.get("bus_api_key", "")): str,
            })

        elif etype == ENTRY_FUEL:
            from .fuel import SIDO_CODES, FUEL_TYPES
            sido_opts = [SelectOptionDict(value=k, label=v) for k, v in SIDO_CODES.items()]
            fuel_opts = [SelectOptionDict(value=k, label=v) for k, v in FUEL_TYPES.items()]
            cur_sidos = list(set(c["sido_code"] for c in d.get("configs", [])))
            cur_fuels = list(set(c["fuel_code"] for c in d.get("configs", [])))
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
                vol.Required("sido_codes", default=cur_sidos): SelectSelector(
                    SelectSelectorConfig(options=sido_opts, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
                vol.Required("fuel_codes", default=cur_fuels): SelectSelector(
                    SelectSelectorConfig(options=fuel_opts, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
            })

        elif etype == ENTRY_SCHOOL:
            import homeassistant.helpers.config_validation as cv
            max_g = 6 if d.get("school_level") == "elementary" else 3
            combo_opts = {}
            for g in range(1, max_g + 1):
                for cl in range(1, 21):
                    combo_opts[f"{g}-{cl}"] = f"{g}학년 {cl}반"
            cur = d.get("grade_classes", [])
            return vol.Schema({
                vol.Required("grade_classes", default=cur): cv.multi_select(combo_opts),
            })

        elif etype == ENTRY_DISASTER:
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
            })

        elif etype == ENTRY_SAFETY_ALERT:
            sido_map = {
                "1100000000": "서울특별시", "2600000000": "부산광역시",
                "2700000000": "대구광역시", "2800000000": "인천광역시",
                "2900000000": "광주광역시", "3000000000": "대전광역시",
                "3100000000": "울산광역시", "3600000000": "세종특별자치시",
                "4100000000": "경기도", "5100000000": "강원특별자치도",
                "4300000000": "충청북도", "4400000000": "충청남도",
                "4500000000": "전북특별자치도", "4600000000": "전라남도",
                "4700000000": "경상북도", "4800000000": "경상남도",
                "5000000000": "제주특별자치도",
            }
            cur_codes = [r["code"] for r in d.get("regions", [])]
            opts = [SelectOptionDict(value=k, label=v) for k, v in sido_map.items()]
            return vol.Schema({
                vol.Required("area_codes", default=cur_codes): SelectSelector(
                    SelectSelectorConfig(options=opts, multiple=True,
                                         mode=SelectSelectorMode.DROPDOWN)),
            })

        elif etype == ENTRY_KEPCO:
            return vol.Schema({
                vol.Required("username", default=d.get("username", "")): str,
                vol.Required("password", default=d.get("password", "")): str,
            })

        elif etype == ENTRY_GASAPP:
            return vol.Schema({
                vol.Required("token", default=d.get("token", "")): str,
                vol.Required("member_id", default=d.get("member_id", "")): str,
                vol.Required("contract_num", default=d.get("contract_num", "")): str,
            })

        elif etype == ENTRY_ARISU:
            return vol.Schema({
                vol.Required("customer_number", default=d.get("customer_number", "")): str,
                vol.Required("customer_name", default=d.get("customer_name", "")): str,
            })

        elif etype == ENTRY_AIRKOREA:
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
                vol.Optional("living_api_key", default=d.get("living_api_key", "")): str,
            })

        elif etype == ENTRY_KMA_WEATHER:
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
            })

        elif etype == ENTRY_EARTHQUAKE:
            return vol.Schema({
                vol.Required("api_key", default=d.get("api_key", "")): str,
                vol.Optional("radius_km", default=d.get("radius_km", 200)): vol.Coerce(int),
                vol.Optional("min_magnitude", default=d.get("min_magnitude", 3.0)): vol.Coerce(float),
            })

        # ENTRY_SEOUL_BUS / ENTRY_KAKAO_BUS are handled by their own menu-
        # driven option flows above; they never reach _build_schema.

        return None
