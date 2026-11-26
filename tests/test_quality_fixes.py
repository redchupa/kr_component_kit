"""Offline regression tests for v4.9.9 quality fixes."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sys
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.helpers.update_coordinator import UpdateFailed

sys.modules.setdefault("xmltodict", SimpleNamespace(parse=Mock()))

from custom_components.kr_component_kit import async_setup_entry
from custom_components.kr_component_kit.const import (
    CONF_ENTRY_TYPE,
    ENTRY_KOREA_BUS,
    ENTRY_SEOUL_BUS,
)
from custom_components.kr_component_kit.disaster.api import (
    DisasterApiError,
    _parse_payload,
    validate_disaster_api,
)
from custom_components.kr_component_kit.disaster.coordinator import DisasterCoordinator
from custom_components.kr_component_kit.fuel import OPINET_AVG_URL, OPINET_LOWPRICE_URL
from custom_components.kr_component_kit.korea_bus.api import KoreaBusApiError
from custom_components.kr_component_kit.korea_bus.coordinator import KoreaBusCoordinator
from custom_components.kr_component_kit.korea_bus.sensor import KoreaBusArrivalSensor
from custom_components.kr_component_kit.korea_bus.switch import KoreaBusActiveSwitch
from custom_components.kr_component_kit.seoul_bus.api import SeoulBusApiError
from custom_components.kr_component_kit.seoul_bus.coordinator import SeoulBusCoordinator
from custom_components.kr_component_kit.seoul_bus.sensor import SeoulBusArrivalSensor
from custom_components.kr_component_kit.seoul_bus.switch import SeoulBusActiveSwitch

KST = timezone(timedelta(hours=9))


class QualityFixesTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.enterContext(patch("homeassistant.helpers.frame.report_usage"))

    def test_opinet_urls_use_https(self):
        self.assertTrue(OPINET_AVG_URL.startswith("https://"))
        self.assertTrue(OPINET_LOWPRICE_URL.startswith("https://"))

    def test_disaster_parse_payload_rejects_xml_and_json_errors(self):
        xml_auth_err = (
            "<response><header>"
            "<resultMsg>SERVICE KEY IS NOT REGISTERED ERROR</resultMsg>"
            "<resultCode>30</resultCode>"
            "<errorMsg>등록되지 않은 서비스키</errorMsg>"
            "</header><body/></response>"
        )
        with self.assertRaises(DisasterApiError):
            _parse_payload(xml_auth_err)

        xml_gateway_err = (
            "<OpenAPI_ServiceResponse><cmmMsgHeader>"
            "<errMsg>SERVICE ERROR</errMsg>"
            "<returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg>"
            "<returnReasonCode>30</returnReasonCode>"
            "</cmmMsgHeader></OpenAPI_ServiceResponse>"
        )
        with self.assertRaises(DisasterApiError):
            _parse_payload(xml_gateway_err)

        json_auth_err = (
            '{"header":{"resultMsg":"SERVICE KEY IS NOT REGISTERED ERROR",'
            '"resultCode":"30","errorMsg":"등록되지 않은 서비스키"},"body":null}'
        )
        with self.assertRaises(DisasterApiError):
            _parse_payload(json_auth_err)

    def test_disaster_parse_payload_accepts_normal_empty_and_rows(self):
        xml_empty = (
            "<response><header>"
            "<resultCode>00</resultCode><resultMsg>NORMAL SERVICE</resultMsg><errorMsg/>"
            "</header><body/></response>"
        )
        self.assertEqual(_parse_payload(xml_empty), [])

        json_empty = '{"header":{"resultCode":"00","resultMsg":"NORMAL SERVICE"},"body":null}'
        self.assertEqual(_parse_payload(json_empty), [])

        xml_rows = (
            "<response><header><resultCode>00</resultCode></header><body>"
            "<row><MSG_CN>호우주의보</MSG_CN><RCPTN_RGN_NM>서울</RCPTN_RGN_NM>"
            "<CRT_DT>2026/11/26 07:00:00</CRT_DT><EMRG_STEP_NM>안전안내</EMRG_STEP_NM>"
            "<DST_SE_NM>호우</DST_SE_NM></row></body></response>"
        )
        rows = _parse_payload(xml_rows)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["message"], "호우주의보")

    def test_disaster_rejects_unknown_envelopes(self):
        for payload in ('[]', 'null', '<html><body>Maintenance</body></html>', '{"error":"maintenance"}',
                        '{"body":[]}', '<response><body/></response>',
                        '{"header":{"resultCode":"00"}}'):
            with self.subTest(payload=payload), self.assertRaises(DisasterApiError):
                _parse_payload(payload)

    def test_discovery_after_setup_registers_each_route_once(self):
        from custom_components.kr_component_kit.bus_routes import register_routes

        coord = Mock(data=None)
        entry, add = Mock(), Mock()
        def factory(coord, route, device_info):
            return route

        register_routes(entry, coord, [], {}, add, [factory])
        add.assert_not_called()
        discover = coord.async_add_listener.call_args.args[0]
        entry.async_on_unload.assert_called_once_with(coord.async_add_listener.return_value)
        coord.data = {"100": {}}
        discover()
        discover()
        add.assert_called_once_with(["100"])
        coord.data["200"] = {}
        discover()
        self.assertEqual(add.call_args.args[0], ["200"])

    async def test_disaster_first_outage_does_not_publish_zero(self):
        from custom_components.kr_component_kit.disaster.sensor import (
            DisasterCountSensor, DisasterMessageSensor,
        )

        coord = DisasterCoordinator(Mock(), "test")
        with patch("custom_components.kr_component_kit.disaster.coordinator.fetch_disaster_messages",
                   side_effect=TimeoutError):
            with self.assertRaises(UpdateFailed):
                await coord._async_update_data()
        owner = SimpleNamespace(coordinator=coord)
        self.assertIsNone(DisasterCountSensor.native_value.fget(owner))
        self.assertIsNone(DisasterMessageSensor.native_value.fget(owner))
        coord.data = []
        self.assertEqual(DisasterCountSensor.native_value.fget(owner), 0)

    async def test_disaster_validate_and_coordinator_fail_on_api_error(self):
        xml_auth_err = (
            "<response><header><resultCode>30</resultCode>"
            "<errorMsg>등록되지 않은 서비스키</errorMsg></header><body/></response>"
        )
        with patch(
            "custom_components.kr_component_kit.disaster.api.paced_curl_request",
            new_callable=AsyncMock,
            return_value=SimpleNamespace(status_code=200, text=xml_auth_err),
        ):
            self.assertFalse(await validate_disaster_api("bad-key"))

            hass = Mock()
            coord = DisasterCoordinator(hass, "bad-key")
            with self.assertRaises(UpdateFailed):
                await coord._async_update_data()

    async def test_seoul_bus_switch_restore_gates_initial_refresh(self):
        coord = SimpleNamespace(
            ars_id="01001",
            api_enabled=False,
            async_request_refresh=AsyncMock(),
        )
        sw = SeoulBusActiveSwitch(coord, {})
        sw.hass = Mock()
        sw.hass.async_create_task = Mock(side_effect=lambda coro: coro.close())

        with patch.object(
            SeoulBusActiveSwitch, "async_get_last_state",
            new_callable=AsyncMock, return_value=SimpleNamespace(state="off"),
        ):
            await sw.async_added_to_hass()
        self.assertFalse(coord.api_enabled)
        sw.hass.async_create_task.assert_not_called()

        with patch.object(
            SeoulBusActiveSwitch, "async_get_last_state",
            new_callable=AsyncMock, return_value=SimpleNamespace(state="on"),
        ):
            await sw.async_added_to_hass()
        self.assertTrue(coord.api_enabled)
        sw.hass.async_create_task.assert_called_once()

    async def test_korea_bus_switch_restore_gates_initial_refresh(self):
        coord = SimpleNamespace(
            stop_id="BS123",
            api_enabled=False,
            async_request_refresh=AsyncMock(),
        )
        sw = KoreaBusActiveSwitch(coord, {})
        sw.hass = Mock()
        sw.hass.async_create_task = Mock(side_effect=lambda coro: coro.close())

        with patch.object(
            KoreaBusActiveSwitch, "async_get_last_state",
            new_callable=AsyncMock, return_value=SimpleNamespace(state="off"),
        ):
            await sw.async_added_to_hass()
        self.assertFalse(coord.api_enabled)
        sw.hass.async_create_task.assert_not_called()

        sw_fresh = KoreaBusActiveSwitch(coord, {})
        sw_fresh.hass = Mock()
        sw_fresh.hass.async_create_task = Mock(side_effect=lambda coro: coro.close())
        with patch.object(
            KoreaBusActiveSwitch, "async_get_last_state",
            new_callable=AsyncMock, return_value=None,
        ):
            await sw_fresh.async_added_to_hass()
        self.assertTrue(coord.api_enabled)
        sw_fresh.hass.async_create_task.assert_called_once()

    async def test_seoul_bus_arrival_timestamp_does_not_drift_during_outage(self):
        t0 = datetime(2026, 11, 26, 10, 0, 0, tzinfo=KST)
        t_later = datetime(2026, 11, 26, 10, 2, 0, tzinfo=KST)
        hass = Mock()
        with patch(
            "custom_components.kr_component_kit.seoul_bus.coordinator.async_get_clientsession",
            return_value=Mock(),
        ):
            coord = SeoulBusCoordinator(hass, "k", "01001", "종로", ["100"])
        self.assertFalse(coord.api_enabled)
        coord.api_enabled = True

        with (
            patch(
                "custom_components.kr_component_kit.seoul_bus.coordinator.fetch_station",
                new_callable=AsyncMock,
                return_value=[{"rtNm": "100", "traTime1": "180", "traTime2": "600"}],
            ),
            patch(
                "custom_components.kr_component_kit.seoul_bus.coordinator.datetime",
            ) as mock_dt,
        ):
            mock_dt.now.return_value = t0
            coord.data = await coord._async_update_data()

        sensor = SeoulBusArrivalSensor(coord, "100", 0, {})
        expected = t0 + timedelta(seconds=180)
        self.assertEqual(sensor.native_value, expected)

        class _LaterDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return t_later

        # Simulate outage 2 minutes later: stale data is returned, arrival stays 10:03.
        with (
            patch(
                "custom_components.kr_component_kit.seoul_bus.coordinator.fetch_station",
                new_callable=AsyncMock,
                side_effect=SeoulBusApiError("timeout"),
            ),
            patch(
                "custom_components.kr_component_kit.seoul_bus.sensor.datetime",
                _LaterDatetime,
            ),
        ):
            coord.data = await coord._async_update_data()
            self.assertEqual(sensor.native_value, expected)

    async def test_korea_bus_arrival_timestamp_does_not_drift_during_outage(self):
        t0 = datetime(2026, 11, 26, 10, 0, 0, tzinfo=KST)
        t_later = datetime(2026, 11, 26, 10, 2, 0, tzinfo=KST)
        hass = Mock()
        with patch(
            "custom_components.kr_component_kit.korea_bus.coordinator.async_get_clientsession",
            return_value=Mock(),
        ):
            coord = KoreaBusCoordinator(hass, "BS123", "강남역", ["360"])
        self.assertFalse(coord.api_enabled)
        coord.api_enabled = True

        with (
            patch(
                "custom_components.kr_component_kit.korea_bus.coordinator.fetch_arrivals",
                new_callable=AsyncMock,
                return_value={"360": {"name": "360", "arrivalTime": 180, "arrivalTime2": 600}},
            ),
            patch(
                "custom_components.kr_component_kit.korea_bus.coordinator.datetime",
            ) as mock_dt,
        ):
            mock_dt.now.return_value = t0
            coord.data = await coord._async_update_data()

        sensor = KoreaBusArrivalSensor(coord, "360", 0, {})
        expected = t0 + timedelta(seconds=180)
        self.assertEqual(sensor.native_value, expected)

        class _LaterDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return t_later

        # Simulate outage 2 minutes later: stale data is returned, arrival stays 10:03.
        with (
            patch(
                "custom_components.kr_component_kit.korea_bus.coordinator.fetch_arrivals",
                new_callable=AsyncMock,
                side_effect=KoreaBusApiError("timeout"),
            ),
            patch(
                "custom_components.kr_component_kit.korea_bus.sensor.datetime",
                _LaterDatetime,
            ),
        ):
            coord.data = await coord._async_update_data()
            self.assertEqual(sensor.native_value, expected)

    async def test_bus_setup_entry_does_not_poll_before_switch_restore(self):
        for etype, payload in (
            (
                ENTRY_SEOUL_BUS,
                {
                    CONF_ENTRY_TYPE: ENTRY_SEOUL_BUS,
                    "api_key": "k",
                    "stations": [{"ars_id": "01001", "station_name": "종로", "routes": ["100"]}],
                },
            ),
            (
                ENTRY_KOREA_BUS,
                {
                    CONF_ENTRY_TYPE: ENTRY_KOREA_BUS,
                    "stops": [{"stop_id": "BS123", "stop_name": "강남역", "routes": ["360"]}],
                },
            ),
        ):
            hass = SimpleNamespace(
                data={},
                config_entries=SimpleNamespace(
                    async_forward_entry_setups=AsyncMock(),
                ),
            )
            entry = SimpleNamespace(
                entry_id=f"entry_{etype}",
                data=payload,
                options={},
                async_on_unload=Mock(),
                add_update_listener=Mock(),
            )
            with (
                patch(
                    "custom_components.kr_component_kit._async_preimport_heavy",
                    new_callable=AsyncMock,
                ),
                patch(
                    "custom_components.kr_component_kit.async_setup_llm_api",
                    new_callable=AsyncMock,
                    return_value=None,
                ),
                patch(
                    "custom_components.kr_component_kit.seoul_bus.coordinator.async_get_clientsession",
                    return_value=Mock(),
                ),
                patch(
                    "custom_components.kr_component_kit.korea_bus.coordinator.async_get_clientsession",
                    return_value=Mock(),
                ),
                patch.object(
                    SeoulBusCoordinator,
                    "async_config_entry_first_refresh",
                    new_callable=AsyncMock,
                ) as seoul_first,
                patch.object(
                    KoreaBusCoordinator,
                    "async_config_entry_first_refresh",
                    new_callable=AsyncMock,
                ) as korea_first,
            ):
                ok = await async_setup_entry(hass, entry)
            self.assertTrue(ok)
            seoul_first.assert_not_awaited()
            korea_first.assert_not_awaited()
            coords = hass.data["kr_component_kit"][entry.entry_id]["coordinators"]
            self.assertTrue(all(not c.api_enabled for c in coords.values()))
