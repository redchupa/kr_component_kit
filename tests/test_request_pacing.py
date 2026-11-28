"""Offline regression tests for outbound pacing and retry behavior."""
import asyncio
from contextlib import asynccontextmanager
from email.utils import formatdate
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

import aiohttp

from custom_components.kr_component_kit import request_pacing as pacing
from custom_components.kr_component_kit.kepco.api import KepcoApiClient, KepcoApiError


class RequestPacingTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.enterContext(patch.object(pacing, "_hosts", {}))
        self.clock = self.enterContext(patch.object(pacing, "time"))
        self.clock.monotonic.return_value = 100
        self.clock.time.return_value = 1000
        self.enterContext(patch.object(pacing.random, "uniform", side_effect=lambda lo, hi: lo))

    async def test_pacing_across_clients_and_hosts(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        @asynccontextmanager
        async def request(method, url, **kwargs):
            entered.set()
            await release.wait()
            yield SimpleNamespace(status=200, headers={})

        async def first():
            async with pacing.paced_request(SimpleNamespace(request=request), "GET", "https://a.test/one"):
                pass

        one = asyncio.create_task(first())
        await entered.wait()
        curl = SimpleNamespace(request=AsyncMock(return_value=SimpleNamespace(status_code=200, headers={})))
        two = asyncio.create_task(pacing.paced_curl_request(curl, "GET", "https://a.test/two"))
        await pacing.paced_curl_request(curl, "GET", "https://b.test/")
        self.assertEqual(curl.request.await_count, 1)
        release.set()
        await one
        # The first request finished at t=100. Advance to the next available slot.
        self.assertEqual(pacing._hosts["a.test"].next_request, 108)
        self.clock.monotonic.return_value = 108
        await two
        self.assertEqual(curl.request.await_count, 2)

    async def test_retry_after_blocks_both_transports_and_recovers(self):
        curl = SimpleNamespace(request=AsyncMock(side_effect=[
            SimpleNamespace(status_code=429, headers={"Retry-After": "180"}),
            SimpleNamespace(status_code=503, headers={"Retry-After": formatdate(1300, usegmt=True)}),
            SimpleNamespace(status_code=200, headers={}),
        ]))
        url = "https://a.test/"
        for now, deadline in [(100, 280), (280, 580)]:
            self.clock.monotonic.return_value = now
            with self.assertRaises(aiohttp.ClientError):
                await pacing.paced_curl_request(curl, "GET", url)
            self.assertEqual(pacing._hosts["a.test"].cooldown_until, deadline)
            with self.assertRaises(aiohttp.ClientError):
                async with pacing.paced_request(None, "GET", url):
                    self.fail("sent during cooldown")
        self.clock.monotonic.return_value = 580
        await pacing.paced_curl_request(curl, "GET", url)
        self.assertEqual(pacing._hosts["a.test"].failures, 0)

    async def test_transport_failure_backs_off_exponentially(self):
        session = SimpleNamespace(request=AsyncMock(side_effect=TimeoutError))
        for now, delay in [(100, 60), (160, 120), (280, 240)]:
            self.clock.monotonic.return_value = now
            with self.assertRaises(TimeoutError):
                await pacing.paced_curl_request(session, "GET", "https://a.test/")
            self.assertEqual(pacing._hosts["a.test"].cooldown_until, now + delay)

    async def test_kepco_only_renews_expired_login(self):
        client = KepcoApiClient(None)
        client.async_login = AsyncMock(return_value=True)
        with patch("custom_components.kr_component_kit.kepco.api.paced_curl_request",
                   new_callable=AsyncMock) as request:
            request.return_value = SimpleNamespace(status_code=200, text="<html>Maintenance</html>")
            with self.assertRaises(KepcoApiError):
                await client.async_get_usage_info()
            client.async_login.assert_not_awaited()
            request.side_effect = [SimpleNamespace(status_code=401, text=""),
                                   SimpleNamespace(status_code=200, text="{}")]
            self.assertEqual(await client.async_get_usage_info(), {})
            client.async_login.assert_awaited_once()

    async def test_pause_is_visible_to_the_user_until_expiry(self):
        hass = Mock()
        self.enterContext(patch.object(pacing, "_notify_cooldown", None))
        create = self.enterContext(patch.object(pacing.ir, "async_create_issue"))
        delete = self.enterContext(patch.object(pacing.ir, "async_delete_issue"))
        pacing.setup_pacing_notices(hass)
        url = "https://a.test/path"
        session = SimpleNamespace(request=AsyncMock(return_value=SimpleNamespace(
            status_code=429, headers={"Retry-After": "240"})))
        with self.assertRaises(aiohttp.ClientError):
            await pacing.paced_curl_request(session, "GET", url)
        self.assertEqual(create.call_args.kwargs["translation_key"], "provider_wait")
        self.assertEqual(create.call_args.kwargs["translation_placeholders"]["host"], "a.test")
        self.clock.monotonic.return_value = 130
        with self.assertRaises(pacing.HomeAssistantError) as error:
            pacing.check_manual_refresh(url)
        self.assertEqual(error.exception.translation_placeholders["seconds"], "210")
        session.request.assert_awaited_once()
        delay, clear = hass.loop.call_later.call_args.args
        self.assertEqual(delay, 240)
        self.clock.monotonic.return_value = 340
        clear()
        delete.assert_called_once_with(hass, pacing.DOMAIN, "provider_wait_a.test")
        pacing.check_manual_refresh(url)

    async def test_single_short_transport_blip_stays_out_of_repairs(self):
        notify = self.enterContext(patch.object(pacing, "_notify_cooldown", Mock()))
        url = "https://a.test/"
        session = SimpleNamespace(request=AsyncMock(side_effect=[
            TimeoutError, SimpleNamespace(status_code=200, headers={}), TimeoutError, TimeoutError,
        ]))
        with self.assertRaises(TimeoutError):
            await pacing.paced_curl_request(session, "GET", url)
        notify.assert_not_called()
        # The pause still applies; a manual refresh explains it without a Repairs notice.
        with self.assertRaises(pacing.HomeAssistantError):
            pacing.check_manual_refresh(url)
        self.clock.monotonic.return_value = 160
        await pacing.paced_curl_request(session, "GET", url)
        self.clock.monotonic.return_value = 168
        with self.assertRaises(TimeoutError):
            await pacing.paced_curl_request(session, "GET", url)
        notify.assert_not_called()
        # A second consecutive failure means the outage is lasting: tell the user.
        self.clock.monotonic.return_value = 228
        with self.assertRaises(TimeoutError):
            await pacing.paced_curl_request(session, "GET", url)
        notify.assert_called_once_with("a.test", 120)
