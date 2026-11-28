"""Offline regression tests for the HACS review fixes (v4.9.14)."""
from __future__ import annotations

from datetime import timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.data_entry_flow import FlowResultType

from custom_components.kr_component_kit.config_flow import KRPublicDataConfigFlow
from custom_components.kr_component_kit.const import CONF_ENTRY_TYPE, DOMAIN, ENTRY_KEPCO
from custom_components.kr_component_kit.kma_weather.coordinator import KMAWeatherCoordinator

KEPCO_COORDINATOR = "custom_components.kr_component_kit.kepco.coordinator.KepcoCoordinator"


class KmaTimezoneTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.enterContext(patch("homeassistant.helpers.frame.report_usage"))

    async def test_update_reuses_setup_timezone_without_building_zoneinfo(self):
        tz = timezone(timedelta(hours=9))
        coord = KMAWeatherCoordinator(
            Mock(), "k", [{"name": "서울", "nx": 60, "ny": 127}], tz, area_no="1100000000")
        base = "custom_components.kr_component_kit"
        with patch(f"{base}.kma_weather.coordinator.fetch_vilage_forecast",
                   new_callable=AsyncMock, return_value=[]), \
             patch(f"{base}.kma_weather.coordinator.parse_weather", return_value={}), \
             patch(f"{base}.airkorea.api.fetch_uv_index",
                   new_callable=AsyncMock, return_value={"h0": "3"}), \
             patch("zoneinfo.ZoneInfo", side_effect=AssertionError("tzdata read on the loop")):
            data = await coord._async_update_data()
        self.assertEqual(data["서울"]["uv_index"], 3.0)


class KepcoReauthTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.entry = SimpleNamespace(entry_id="e1", data={
            CONF_ENTRY_TYPE: ENTRY_KEPCO, "username": "user1", "password": "old"})
        self.flow = KRPublicDataConfigFlow()
        self.flow.hass = Mock()
        self.flow.hass.config_entries.async_get_entry.return_value = self.entry
        self.flow.handler = DOMAIN
        self.flow.flow_id = "flow1"
        self.flow.context = {"source": "reauth", "entry_id": "e1"}

    def _login(self, **kwargs):
        return patch(KEPCO_COORDINATOR, return_value=SimpleNamespace(
            async_login=AsyncMock(**kwargs)))

    async def test_reauth_shows_password_form_for_saved_account(self):
        result = await self.flow.async_step_reauth(self.entry.data)
        self.assertEqual(result["type"], FlowResultType.FORM)
        self.assertEqual(result["step_id"], "reauth_confirm")
        # HA adds its own "name" placeholder for reauth forms; ours is the account.
        self.assertEqual(result["description_placeholders"]["username"], "user1")
        self.assertEqual(list(result["data_schema"].schema), ["password"])

    async def test_reauth_reports_rejected_or_unreachable_login(self):
        for kwargs, error in [({"return_value": False}, "invalid_auth"),
                              ({"side_effect": TimeoutError}, "cannot_connect")]:
            with self._login(**kwargs):
                result = await self.flow.async_step_reauth_confirm({"password": "x"})
            self.assertEqual(result["errors"], {"base": error})

    async def test_reauth_updates_password_and_reloads(self):
        self.flow.async_update_reload_and_abort = Mock(return_value="aborted")
        with self._login(return_value=True) as coordinator:
            result = await self.flow.async_step_reauth_confirm({"password": "new"})
        self.assertEqual(result, "aborted")
        coordinator.assert_called_once_with(self.flow.hass, "user1", "new")
        self.flow.async_update_reload_and_abort.assert_called_once_with(
            self.entry, data={**self.entry.data, "password": "new"})

    def test_reauth_strings_present_in_all_translations(self):
        base = Path("custom_components/kr_component_kit")
        for rel in ("strings.json", "translations/en.json",
                    "translations/ko.json", "translations/ja.json"):
            config = json.loads((base / rel).read_text(encoding="utf-8"))["config"]
            step = config["step"]["reauth_confirm"]
            self.assertIn("{username}", step["description"], rel)
            self.assertIn("password", step["data"], rel)
            self.assertIn("reauth_successful", config["abort"], rel)
