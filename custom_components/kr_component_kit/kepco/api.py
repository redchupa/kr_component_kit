"""KEPCO API client - NO module-level curl_cffi import."""
from __future__ import annotations
import json
import logging

from .exceptions import KepcoApiError, KepcoAuthError

_LOGGER = logging.getLogger(__name__)

# Markers in the post-login URL or body that signal an authenticated session.
# We accept any of these so a cosmetic page rename on KEPCO's side doesn't
# silently break login detection. As of 2026 the redirect lands on
# `confirmInfo.do` (account confirmation) or `myInfo.do` (profile dashboard).
_LOGIN_OK_URL_MARKERS = ("confirmInfo.do", "myInfo.do", "/main/main.do")
_LOGIN_FAIL_BODY_MARKERS = ("로그인 실패", "비밀번호가 일치하지 않", "존재하지 않는 아이디")


def _get_rsa_key():
    """Lazy import RSAKey to avoid triggering utils import chain."""
    from ..utils import RSAKey
    return RSAKey


class KepcoApiClient:
    def __init__(self, session):
        self._session = session
        self._username = None
        self._password = None

    def set_credentials(self, username, password):
        self._username = username
        self._password = password

    async def async_get_session_and_rsa_key(self):
        from bs4 import BeautifulSoup  # lazy import
        url = "https://pp.kepco.co.kr:8030/intro.do"
        result = await self._session.get(url=url)
        result.raise_for_status()
        html_text = result.text
        soup = BeautifulSoup(html_text, "html.parser")
        rsa_modulus_tag = soup.find("input", {"id": "RSAModulus"})
        rsa_exponent_tag = soup.find("input", {"id": "RSAExponent"})
        sessid_tag = soup.find("input", {"id": "SESSID"})
        if not rsa_modulus_tag or not rsa_exponent_tag or not sessid_tag:
            raise KepcoAuthError("Failed to get RSA keys from intro page")
        return (rsa_modulus_tag.get("value").strip(),
                rsa_exponent_tag.get("value").strip(),
                sessid_tag.get("value").strip())

    async def async_login(self, username, password):
        self.set_credentials(username, password)
        try:
            rsa_modulus, rsa_exponent, sessid = await self.async_get_session_and_rsa_key()
        except KepcoAuthError:
            return False
        RSAKey = _get_rsa_key()
        try:
            rsa_key = RSAKey()
            rsa_key.set_public(rsa_modulus, rsa_exponent)
            enc_user = rsa_key.encrypt(username)
            enc_pass = rsa_key.encrypt(password)
            if not enc_user or not enc_pass:
                raise ValueError("RSA encryption failed")
        except Exception as e:
            _LOGGER.error("RSA encryption failed: %s", e)
            return False
        user_id = f"{sessid}_{enc_user}"
        user_pw = f"{sessid}_{enc_pass}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://pp.kepco.co.kr:8030/intro.do",
            "Cookie": f"JSESSIONID={sessid}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        }
        try:
            response = await self._session.post(
                "https://pp.kepco.co.kr:8030/login",
                data={"USER_ID": user_id, "USER_PW": user_pw},
                headers=headers, allow_redirects=True)
        except Exception as e:
            _LOGGER.error("KEPCO login HTTP failed: %s", e)
            return False
        if response.status_code != 200:
            _LOGGER.warning("KEPCO login HTTP %s", response.status_code)
            return False
        url_str = str(response.url)
        if any(marker in url_str for marker in _LOGIN_OK_URL_MARKERS):
            return True
        body = response.text or ""
        for marker in _LOGIN_FAIL_BODY_MARKERS:
            if marker in body:
                _LOGGER.warning("KEPCO login rejected: %s", marker)
                return False
        # Unknown post-login state — log a snippet so we can update markers
        # if KEPCO renames the redirect target.
        _LOGGER.warning(
            "KEPCO login: unknown redirect %s, body[:200]=%s",
            url_str, body[:200].strip(),
        )
        return False

    async def _request(self, method, url, **kwargs):
        """Issue a request, retrying once with re-login on auth-shaped failures.

        We **only** retry on JSON-decode failures (typical KEPCO behaviour for
        an expired session — the gateway returns the login HTML with status
        200), not on every exception. Network errors and HTTP errors must
        propagate so transient outages aren't mistaken for bad credentials,
        which would otherwise hammer the login endpoint and risk lockout.
        """
        response = await self._session.request(method, url, **kwargs)
        try:
            return json.loads(response.text)
        except (json.JSONDecodeError, ValueError):
            # Likely the session expired and we got an HTML page back.
            _LOGGER.debug("KEPCO request %s returned non-JSON; re-login + retry", url)
            if not await self.async_login(self._username, self._password):
                raise KepcoAuthError("Re-login failed during retry")
            response = await self._session.request(method, url, **kwargs)
            try:
                return json.loads(response.text)
            except (json.JSONDecodeError, ValueError) as e:
                snippet = (response.text or "")[:200].strip()
                raise KepcoApiError(
                    f"KEPCO 응답이 JSON이 아닙니다 (재로그인 후): {snippet}"
                ) from e

    async def async_get_recent_usage(self):
        return await self._request("POST", "https://pp.kepco.co.kr:8030/low/main/recent_usage.do", json={})

    async def async_get_usage_info(self):
        return await self._request("POST", "https://pp.kepco.co.kr:8030/low/main/usage_info.do", json={"tou": "N"})
