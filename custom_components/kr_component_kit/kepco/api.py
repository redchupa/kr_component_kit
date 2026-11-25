"""KEPCO API client - NO module-level curl_cffi import."""
from __future__ import annotations

import json
import logging

from ..request_pacing import paced_curl_request
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
        result = await paced_curl_request(self._session, "GET", url=url)
        result.raise_for_status()
        html_text = result.text
        soup = BeautifulSoup(html_text, "html.parser")
        rsa_modulus_tag = soup.find("input", {"id": "RSAModulus"})
        rsa_exponent_tag = soup.find("input", {"id": "RSAExponent"})
        sessid_tag = soup.find("input", {"id": "SESSID"})
        if not rsa_modulus_tag or not rsa_exponent_tag or not sessid_tag:
            raise KepcoApiError("Failed to get RSA keys from intro page")
        return (rsa_modulus_tag.get("value").strip(),
                rsa_exponent_tag.get("value").strip(),
                sessid_tag.get("value").strip())

    async def async_login(self, username, password):
        self.set_credentials(username, password)
        rsa_modulus, rsa_exponent, sessid = await self.async_get_session_and_rsa_key()
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
        response = await paced_curl_request(
            self._session, "POST", "https://pp.kepco.co.kr:8030/login",
            data={"USER_ID": user_id, "USER_PW": user_pw},
            headers=headers, allow_redirects=True,
        )
        if response.status_code == 401:
            return False
        if response.status_code != 200:
            raise KepcoApiError(f"KEPCO login HTTP {response.status_code}")
        url_str = str(response.url)
        if any(marker in url_str for marker in _LOGIN_OK_URL_MARKERS):
            return True
        body = response.text or ""
        for marker in _LOGIN_FAIL_BODY_MARKERS:
            if marker in body:
                _LOGGER.warning("KEPCO login rejected: %s", marker)
                return False
        raise KepcoApiError("KEPCO login returned an unrecognized page")

    async def _request(self, method, url, **kwargs):
        """Renew an expired login once, only for an identifiable login response."""
        for attempt in range(2):
            response = await paced_curl_request(self._session, method, url, **kwargs)
            login_page = response.status_code == 401 or (
                response.status_code == 200
                and "RSAModulus" in response.text
                and "SESSID" in response.text
            )
            if login_page:
                if attempt or not await self.async_login(self._username, self._password):
                    raise KepcoAuthError("KEPCO session could not be renewed")
                continue
            if response.status_code != 200:
                raise KepcoApiError(f"KEPCO usage HTTP {response.status_code}")
            try:
                return json.loads(response.text)
            except ValueError as err:
                raise KepcoApiError("KEPCO usage response was not JSON") from err

    async def async_get_recent_usage(self):
        return await self._request("POST", "https://pp.kepco.co.kr:8030/low/main/recent_usage.do", json={})

    async def async_get_usage_info(self):
        return await self._request("POST", "https://pp.kepco.co.kr:8030/low/main/usage_info.do", json={"tou": "N"})
