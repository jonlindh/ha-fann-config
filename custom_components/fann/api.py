"""FANN Config API."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp

from .const import DYNAMIC_URL, LOGIN_URL, ZZZ_URL
from .models import FannDevice
from .parser import parse_dynamic

_LOGGER = logging.getLogger(__name__)


class FannApiError(Exception):
    """Base FANN API error."""


class FannAuthError(FannApiError):
    """FANN authentication error."""


class FannApi:
    """FANN Config API."""

    def __init__(self, serial: str, key: str) -> None:
        self._serial = serial
        self._key = key
        self._session: aiohttp.ClientSession | None = None
        self._logged_in = False

    async def connect(self) -> None:
        """Create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._logged_in = False

    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

        self._session = None
        self._logged_in = False

    async def login(self) -> None:
        """Login to FANN."""
        await self.connect()

        _LOGGER.debug("Logging in to FANN")

        await self._raw_request(
            "POST",
            LOGIN_URL,
            data={
                "serial": self._serial,
                "key": self._key,
            },
        )

        self._logged_in = True
        _LOGGER.debug("Logged in to FANN")

    async def ensure_login(self) -> None:
        """Ensure login session."""
        if not self._logged_in:
            await self.login()

    async def get_devices(self) -> list[FannDevice]:
        """Get FANN devices."""
        text = await self._request("GET", DYNAMIC_URL)

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise FannApiError("Could not parse FANN device response") from err

        if not payload or "data" not in payload[0]:
            raise FannApiError("Unexpected FANN device response")

        devices = parse_dynamic(payload[0]["data"])

        _LOGGER.debug("Found %d FANN devices", len(devices))

        for device in devices:
            _LOGGER.debug(
                "FANN device: dbid=%s model=%s nickname=%s connected=%s state=%s raw_status=%s",
                device.dbid,
                device.model,
                device.nickname,
                device.connected,
                device.state,
                device.raw_status,
            )

        return devices

    async def wake(self, dbid: int) -> None:
        """Wake device."""
        await self.set_state(dbid, "W")

    async def sleep(self, dbid: int) -> None:
        """Put device to sleep."""
        await self.set_state(dbid, "Z")

    async def set_state(self, dbid: int, state: str) -> None:
        """Set device state."""
        
        _LOGGER.debug("Setting FANN device %s to state %s", dbid, state)

        await self._request(
            "GET",
            ZZZ_URL,
            params={
                "id": dbid,
                "state": state,
            },
        )

    async def _request(
        self,
        method: str,
        url: str,
        retry: bool = True,
        **kwargs: Any,
    ) -> str:
        """Authenticated request with one retry."""
        await self.ensure_login()

        text = await self._raw_request(method, url, **kwargs)

        if self._looks_like_login_page(text):
            if retry:
                _LOGGER.debug("FANN session expired, logging in again")
                self._logged_in = False
                await self.login()
                return await self._request(method, url, retry=False, **kwargs)

            self._logged_in = False
            raise FannAuthError("FANN session expired")

        return text

    async def _raw_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> str:
        """Raw HTTP request."""
        await self.connect()

        if self._session is None:
            raise FannApiError("HTTP session not available")

        async with self._session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.text()

    @staticmethod
    def _looks_like_login_page(text: str) -> bool:
        """Return true if response appears to be the login page."""
        lowered = text.lower()
        return "login" in lowered and ("serial" in lowered or "password" in lowered)