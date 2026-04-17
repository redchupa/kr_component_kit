from __future__ import annotations

from typing import Any, Dict, Optional

import aiohttp
import curl_cffi
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback

from .arisu.api import ArisuApiClient
from .arisu.exceptions import ArisuAuthError
from .const import DOMAIN, LOGGER
from .gasapp.api import GasAppApiClient
from .gasapp.exceptions import GasAppAuthError
from .goodsflow.api import GoodsFlowApiClient
from .goodsflow.exceptions import GoodsFlowAuthError
from .kakaomap.api import KakaoMapApiClient
from .kakaomap.coordinates import convert_coordinates, validate_coordinates
from .kakaomap.exceptions import KakaoMapConnectionError
from .kepco.api import KepcoApiClient
from .kepco.exceptions import KepcoAuthError
from .safety_alert.api import SafetyAlertApiClient
from .safety_alert.exceptions import SafetyAlertConnectionError
from .safety_alert.region_api import SafetyAlertRegionApiClient


class KoreaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Korea integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._safety_alert_data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        return self.async_show_menu(
            step_id="user",
            menu_options=[
                "kepco",
                "gasapp",
                "safety_alert",
                "goodsflow",
                "arisu",
                "kakaomap",
            ],
        )

    async def async_step_kepco(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle KEPCO configuration."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            async with curl_cffi.AsyncSession() as session:
                client = KepcoApiClient(session)
                client.set_credentials(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                try:
                    if await client.async_login(
                        user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                    ):
                        unique_id = f"kepco_{user_input[CONF_USERNAME]}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        user_input["service"] = "kepco"
                        return self.async_create_entry(
                            title=f"한전 ({user_input[CONF_USERNAME]})", data=user_input
                        )
                    else:
                        errors["base"] = "auth"
                        error_info["error"] = "Login returned false"
                except KepcoAuthError as e:
                    LOGGER.error(f"KEPCO login failed: {e}")
                    errors["base"] = "invalid_auth"
                    error_info["error"] = str(e)
                except Exception as e:
                    LOGGER.error(f"KEPCO login failed: {e}")
                    errors["base"] = "unknown"
                    error_info["error"] = str(e)

        return self.async_show_form(
            step_id="kepco",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    async def async_step_gasapp(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle GasApp configuration."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            async with aiohttp.ClientSession() as session:
                client = GasAppApiClient(session)
                client.set_credentials(
                    user_input["token"],
                    user_input["member_id"],
                    user_input["use_contract_num"],
                )
                try:
                    if await client.async_validate_credentials():
                        unique_id = f"gasapp_{user_input['use_contract_num']}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        user_input["service"] = "gasapp"
                        return self.async_create_entry(
                            title=f"가스앱 ({user_input['use_contract_num']})",
                            data=user_input,
                        )
                    else:
                        errors["base"] = "auth"
                        error_info["error"] = "Credential validation returned false"
                except GasAppAuthError as e:
                    LOGGER.error(f"GasApp authentication failed: {e}")
                    errors["base"] = "invalid_auth"
                    error_info["error"] = str(e)
                except Exception as e:
                    LOGGER.error(f"GasApp connection failed: {e}")
                    errors["base"] = "unknown"
                    error_info["error"] = str(e)

        return self.async_show_form(
            step_id="gasapp",
            data_schema=vol.Schema(
                {
                    vol.Required("token"): str,
                    vol.Required("member_id"): str,
                    vol.Required("use_contract_num"): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    async def async_step_safety_alert(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Handle Safety Alert configuration - start with sido selection."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            sido_code = user_input["sido_code"]
            sido_name = self._safety_alert_data.get("sido_options", {}).get(sido_code, sido_code)
            self._safety_alert_data["sido_code"] = sido_code
            self._safety_alert_data["sido_name"] = sido_name
            return await self.async_step_safety_alert_sgg()

        # Get sido list
        try:
            async with aiohttp.ClientSession() as session:
                region_client = SafetyAlertRegionApiClient(session)
                sido_list = await region_client.async_get_sido_list()

                if not sido_list:
                    errors["base"] = "no_regions_available"
                    error_info["error"] = "No sido data returned from API"
                else:
                    sido_options = {
                        region["code"]: region["name"] for region in sido_list
                    }
                    self._safety_alert_data["sido_options"] = sido_options

                    return self.async_show_form(
                        step_id="safety_alert",
                        data_schema=vol.Schema(
                            {
                                vol.Required("sido_code", default="1100000000"): vol.In(
                                    sido_options
                                ),
                            }
                        ),
                        errors=errors,
                        description_placeholders=error_info,
                    )

        except SafetyAlertConnectionError as e:
            LOGGER.error(f"Safety Alert region API failed: {e}")
            errors["base"] = "cannot_connect"
            error_info["error"] = str(e)
        except Exception as e:
            LOGGER.error(f"Safety Alert setup failed: {e}")
            errors["base"] = "unknown"
            error_info["error"] = str(e)

        return self.async_show_form(
            step_id="safety_alert",
            data_schema=vol.Schema(
                {
                    vol.Required("sido_code", default="1100000000"): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    async def async_step_safety_alert_sgg(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Handle Safety Alert sgg (시군구) selection."""
        if user_input is not None:
            sgg_code = user_input.get("sgg_code") or user_input.get("sgg_name", "")
            sgg_name = (
                self._safety_alert_data.get("sgg_options", {}).get(sgg_code, sgg_code)
            )
            self._safety_alert_data["sgg_code"] = sgg_code
            self._safety_alert_data["sgg_name"] = sgg_name
            if user_input.get("add_emd", False):
                return await self.async_step_safety_alert_emd()
            else:
                return await self._create_safety_alert_entry()

        sido_code = self._safety_alert_data.get("sido_code", "")
        sido_name = self._safety_alert_data.get("sido_name", "")

        region_client = SafetyAlertRegionApiClient()
        sgg_list = await region_client.async_get_sgg_list(sido_code)

        if sgg_list:
            sgg_options = {r["code"]: r["name"] for r in sgg_list}
            self._safety_alert_data["sgg_options"] = sgg_options
            return self.async_show_form(
                step_id="safety_alert_sgg",
                data_schema=vol.Schema(
                    {
                        vol.Required("sgg_code"): vol.In(sgg_options),
                        vol.Optional("add_emd", default=False): bool,
                    }
                ),
                description_placeholders={"sido_name": sido_name},
            )

        # No hardcoded data for this sido — fall back to manual text input
        return self.async_show_form(
            step_id="safety_alert_sgg",
            data_schema=vol.Schema(
                {
                    vol.Required("sgg_name"): str,
                    vol.Optional("add_emd", default=False): bool,
                }
            ),
            description_placeholders={"sido_name": sido_name},
        )

    async def async_step_safety_alert_emd(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Handle Safety Alert emd (읍면동) manual input."""
        if user_input is not None:
            self._safety_alert_data["emd_name"] = user_input["emd_name"]
            return await self._create_safety_alert_entry()

        sgg_name = self._safety_alert_data.get("sgg_name", "")
        return self.async_show_form(
            step_id="safety_alert_emd",
            data_schema=vol.Schema(
                {
                    vol.Required("emd_name"): str,
                }
            ),
            description_placeholders={"sgg_name": sgg_name},
        )

    async def _create_safety_alert_entry(self):
        """Create the safety alert config entry."""
        try:
            sido_code = self._safety_alert_data["sido_code"]
            sgg_code = self._safety_alert_data.get("sgg_code", "")
            sgg_name = self._safety_alert_data.get("sgg_name", "")
            emd_name = self._safety_alert_data.get("emd_name", "")

            # Use sgg_code for API filtering only if it looks like a numeric code
            api_area_code2 = sgg_code if sgg_code.isdigit() else None

            async with aiohttp.ClientSession() as session:
                client = SafetyAlertApiClient(session)
                await client.async_get_safety_alerts(sido_code, api_area_code2)

            display_name = self._safety_alert_data["sido_name"]
            if sgg_name:
                display_name += f" {sgg_name}"
            if emd_name:
                display_name += f" {emd_name}"

            unique_id = f"safety_alert_{sido_code}_{sgg_code}_{emd_name}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            entry_data = {
                "service": "safety_alert",
                "area_code": sido_code,
                "area_name": display_name,
                "sido_code": sido_code,
                "sido_name": self._safety_alert_data["sido_name"],
            }
            if sgg_code:
                entry_data["area_code2"] = api_area_code2 or ""
                entry_data["area_name2"] = sgg_name
            if emd_name:
                entry_data["area_name3"] = emd_name

            return self.async_create_entry(
                title=f"안전알림 ({display_name})", data=entry_data
            )

        except SafetyAlertConnectionError as e:
            LOGGER.error(f"Safety Alert connection failed: {e}")
            return self.async_abort(reason="cannot_connect")
        except Exception as e:
            LOGGER.error(f"Safety Alert setup failed: {e}")
            return self.async_abort(reason="unknown")

    async def async_step_arisu(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle Arisu configuration."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            async with aiohttp.ClientSession() as session:
                client = ArisuApiClient(session)
                try:
                    # Test the API with the provided credentials (both customer number and name)
                    bill_data = await client.async_get_water_bill_data(
                        user_input["customer_number"], user_input["customer_name"]
                    )

                    if bill_data.get("success", False):
                        unique_id = f"arisu_{user_input['customer_number']}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        user_input["service"] = "arisu"
                        return self.async_create_entry(
                            title=f"아리수 ({user_input['customer_number']})",
                            data=user_input,
                        )
                    else:
                        errors["base"] = "invalid_auth"
                        error_info["error"] = "Credentials validation failed"
                except ArisuAuthError as e:
                    LOGGER.error(f"Arisu authentication failed: {e}")
                    errors["base"] = "invalid_auth"
                    error_info["error"] = str(e)
                except Exception as e:
                    LOGGER.error(f"Arisu connection failed: {e}")
                    errors["base"] = "unknown"
                    error_info["error"] = str(e)

        return self.async_show_form(
            step_id="arisu",
            data_schema=vol.Schema(
                {
                    vol.Required("customer_number"): str,
                    vol.Required("customer_name"): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    async def async_step_kakaomap(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle KakaoMap configuration."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            async with aiohttp.ClientSession() as session:
                client = KakaoMapApiClient(session)
                try:
                    # 좌표계 변환 처리
                    coord_system = user_input.get("coord_system", "WCONGNAMUL")

                    # 입력 좌표 준비
                    if coord_system == "WGS84":
                        # WGS84 좌표를 입력받은 경우
                        start_coords_input = {
                            "longitude": float(user_input["start_x"]),
                            "latitude": float(user_input["start_y"]),
                        }
                        end_coords_input = {
                            "longitude": float(user_input["end_x"]),
                            "latitude": float(user_input["end_y"]),
                        }

                        # 좌표 유효성 검사
                        if not validate_coordinates(start_coords_input, "WGS84"):
                            errors["start_x"] = "invalid_wgs84_coordinates"
                            error_info["error"] = (
                                f"Longitude: {start_coords_input['longitude']}, Latitude: {start_coords_input['latitude']}"
                            )
                        if not validate_coordinates(end_coords_input, "WGS84"):
                            errors["end_x"] = "invalid_wgs84_coordinates"
                            error_info["error"] = (
                                f"Longitude: {end_coords_input['longitude']}, Latitude: {end_coords_input['latitude']}"
                            )

                        if not errors:
                            # WGS84를 WCONGNAMUL로 변환
                            start_coords = convert_coordinates(
                                start_coords_input, "WGS84", "WCONGNAMUL"
                            )
                            end_coords = convert_coordinates(
                                end_coords_input, "WGS84", "WCONGNAMUL"
                            )
                    else:
                        # WCONGNAMUL 좌표를 입력받은 경우
                        start_coords = {
                            "x": float(user_input["start_x"]),
                            "y": float(user_input["start_y"]),
                        }
                        end_coords = {
                            "x": float(user_input["end_x"]),
                            "y": float(user_input["end_y"]),
                        }

                        # 좌표 유효성 검사
                        if not validate_coordinates(start_coords, "WCONGNAMUL"):
                            errors["start_x"] = "invalid_wcongnamul_coordinates"
                            error_info["error"] = (
                                f"X: {start_coords['x']}, Y: {start_coords['y']}"
                            )
                        if not validate_coordinates(end_coords, "WCONGNAMUL"):
                            errors["end_x"] = "invalid_wcongnamul_coordinates"
                            error_info["error"] = (
                                f"X: {end_coords['x']}, Y: {end_coords['y']}"
                            )

                    if not errors:
                        # Test coordinate to address conversion
                        start_address = await client.async_coordinate_to_address(
                            start_coords["x"], start_coords["y"]
                        )

                        if start_address.get("success"):
                            unique_id = (
                                f"kakaomap_{user_input['name'].replace(' ', '_')}"
                            )
                            await self.async_set_unique_id(unique_id)
                            self._abort_if_unique_id_configured()

                            user_input["service"] = "kakaomap"
                            user_input["start_coords"] = start_coords
                            user_input["end_coords"] = end_coords
                            # 원본 좌표계 정보도 저장 (참고용)
                            user_input["original_coord_system"] = coord_system

                            return self.async_create_entry(
                                title=f"카카오맵 ({user_input['name']})",
                                data=user_input,
                            )
                        else:
                            errors["base"] = "invalid_coordinates"
                            error_info["error"] = (
                                "Address lookup failed with the provided coordinates"
                            )

                except KakaoMapConnectionError as e:
                    LOGGER.error(f"KakaoMap connection failed: {e}")
                    errors["base"] = "cannot_connect"
                    error_info["error"] = str(e)
                except ValueError as e:
                    LOGGER.error(f"Invalid coordinates: {e}")
                    errors["base"] = "invalid_coordinates"
                    error_info["error"] = str(e)
                except Exception as e:
                    LOGGER.error(f"KakaoMap setup failed: {e}")
                    errors["base"] = "unknown"
                    error_info["error"] = str(e)

        return self.async_show_form(
            step_id="kakaomap",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default="집↔회사"): str,
                    vol.Required("coord_system", default="WCONGNAMUL"): vol.In(
                        ["WCONGNAMUL", "WGS84"]
                    ),
                    vol.Required(
                        "start_x", default="515290"
                    ): str,  # 기본값: WCONGNAMUL 건대입구역
                    vol.Required("start_y", default="1122478"): str,
                    vol.Required(
                        "end_x", default="506190"
                    ): str,  # 기본값: WCONGNAMUL 강남역
                    vol.Required("end_y", default="1110730"): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    async def async_step_goodsflow(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle GoodsFlow configuration."""
        errors: Dict[str, str] = {}
        error_info: Dict[str, str] = {}

        if user_input is not None:
            async with aiohttp.ClientSession() as session:
                client = GoodsFlowApiClient(session)
                client.set_token(user_input["token"])
                try:
                    if await client.async_validate_token():
                        unique_id = f"goodsflow_{user_input['token'][:8]}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        user_input["service"] = "goodsflow"
                        return self.async_create_entry(
                            title="굿스플로우 택배조회", data=user_input
                        )
                    else:
                        errors["base"] = "invalid_auth"
                        error_info["error"] = "Token validation failed"
                except GoodsFlowAuthError as e:
                    LOGGER.error(f"GoodsFlow authentication failed: {e}")
                    errors["base"] = "invalid_auth"
                    error_info["error"] = str(e)
                except Exception as e:
                    LOGGER.error(f"GoodsFlow connection failed: {e}")
                    errors["base"] = "unknown"
                    error_info["error"] = str(e)

        return self.async_show_form(
            step_id="goodsflow",
            data_schema=vol.Schema(
                {
                    vol.Required("token"): str,
                }
            ),
            errors=errors,
            description_placeholders=error_info,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return KoreaOptionsFlow(config_entry)


class KoreaOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Korea integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None):
        """Manage the options."""
        service = self.config_entry.data.get("service")
        if service == "kepco":
            return self.async_abort(reason="no_options_kepco")
        elif service == "gasapp":
            return self.async_abort(reason="no_options_gasapp")
        elif service == "safety_alert":
            return self.async_abort(reason="no_options_safety_alert")
        elif service == "goodsflow":
            return self.async_abort(reason="no_options_goodsflow")
        elif service == "arisu":
            return self.async_abort(reason="no_options_arisu")
        elif service == "kakaomap":
            return self.async_abort(reason="no_options_kakaomap")

        return self.async_abort(reason="no_options")
