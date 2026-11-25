"""Outbound request pacing shared by all integration entries in this HA process."""
from __future__ import annotations

import asyncio
import math
import random
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import aiohttp
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import DOMAIN


@dataclass
class _Host:
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    next_request: float = 0
    cooldown_until: float = 0
    failures: int = 0

    def record_failure(self, host, retry_after=None):
        self.failures = min(6, self.failures + 1)
        delay = 60 * 2 ** (self.failures - 1)
        if retry_after:
            try:
                if retry_after.strip().isascii() and retry_after.strip().isdigit():
                    seconds = float(retry_after)
                else:
                    seconds = parsedate_to_datetime(retry_after).timestamp() - time.time()
                delay = max(delay, seconds)
            except (TypeError, ValueError, OverflowError, OSError):
                pass
        delay += random.uniform(0, 10)
        self.cooldown_until = time.monotonic() + delay
        if _notify_cooldown is not None:
            _notify_cooldown(host, delay)

    def check_response(self, host, status, headers):
        if status == 429 or 500 <= status < 600:
            self.record_failure(host, headers.get("Retry-After"))
            raise aiohttp.ClientError(f"{host} returned HTTP {status}")


_hosts: dict[str, _Host] = {}


_notify_cooldown = None


def setup_pacing_notices(hass):
    """Show one temporary Repairs notice per host, in the user's language."""
    global _notify_cooldown

    clear_timers = {}

    def notify(host, delay):
        issue_id = f"provider_wait_{host}"
        try:
            retry_at = (dt_util.as_local(dt_util.utcnow() + timedelta(seconds=delay))
                        .strftime("%Y-%m-%d %H:%M:%S %Z"))
        except OverflowError:
            retry_at = "∞"
        ir.async_create_issue(
            hass, DOMAIN, issue_id, is_fixable=False, severity=ir.IssueSeverity.WARNING,
            translation_key="provider_wait", translation_placeholders={
                "host": host, "retry_at": retry_at,
            },
        )

        def clear_when_due():
            clear_timers.pop(host, None)
            ir.async_delete_issue(hass, DOMAIN, issue_id)

        previous = clear_timers.pop(host, None)
        if previous is not None:
            previous.cancel()

        if math.isfinite(delay):
            clear_timers[host] = hass.loop.call_later(delay, clear_when_due)

    _notify_cooldown = notify


def check_manual_refresh(url):
    """Explain an active cooldown in the action response without sending a request."""
    host = urlsplit(url).hostname
    state = _hosts.get(host)
    if state and (remaining := state.cooldown_until - time.monotonic()) > 0:
        seconds = str(math.ceil(remaining)) if math.isfinite(remaining) else "∞"
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="refresh_wait",
            translation_placeholders={"host": host, "seconds": seconds},
        )


@asynccontextmanager
async def _slot(url):
    host = urlsplit(url).hostname
    if host not in _hosts:
        # Spread first polls when many installations restart together.
        _hosts[host] = _Host(next_request=time.monotonic() + random.uniform(0, 15))
    state = _hosts[host]
    # Discard obsolete queued work if the host remains saturated.
    try:
        async with asyncio.timeout(90):
            await state.lock.acquire()
    except TimeoutError as err:
        raise aiohttp.ClientError(f"{host} request queue is busy") from err
    try:
        if time.monotonic() < state.cooldown_until:
            raise aiohttp.ClientError(f"{host} is cooling down after an upstream failure")
        await asyncio.sleep(max(0, state.next_request - time.monotonic()))
        try:
            yield host, state
        finally:
            state.next_request = time.monotonic() + random.uniform(8, 12)
    finally:
        state.lock.release()


@asynccontextmanager
async def paced_request(session, method, url, **kwargs):
    """Serialize aiohttp requests through body consumption, outside the I/O timeout."""
    async with _slot(url) as (host, state):
        kwargs.setdefault("timeout", aiohttp.ClientTimeout(total=30))
        try:
            async with session.request(method, url, **kwargs) as response:
                state.check_response(host, response.status, response.headers)
                yield response
                state.failures = 0
        except (aiohttp.ClientConnectionError, TimeoutError):
            state.record_failure(host)
            raise


async def paced_curl_request(session, method, url, **kwargs):
    """curl_cffi buffers the body before returning the response."""
    async with _slot(url) as (host, state):
        kwargs.setdefault("timeout", 30)
        try:
            response = await session.request(method, url, **kwargs)
        except Exception:
            state.record_failure(host)
            raise
        state.check_response(host, response.status_code, response.headers)
        state.failures = 0
        return response
