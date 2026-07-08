"""FANN Config API."""

from __future__ import annotations

import json
import logging

import aiohttp

from .const import DYNAMIC_URL, LOGIN_URL, ZZZ_URL
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

        _LOGGER.debug("Logging into FANN")

        async with self._session.post(
            LOGIN_URL,
            data={
                "serial": self._serial,
                "key": self._key,
            },
        ) as response:
            response.raise_for_status()
            text = await response.text()

        if "login" in text.lower() and "not available" in text.lower():
            raise FannAuthError("FANN login failed")

        self._logged_in = True

    async def ensure_login(self) -> None:
        """Ensure active login session."""
        if self._logged_in:
            return

        await self.login()

    async def get_devices(self):
        """Download and parse devices."""
        return await self._get_devices_with_retry()

    async def _get_devices_with_retry(self, retry: bool = True):
        """Download devices and retry once if session expired."""
        await self.ensure_login()

        _LOGGER.debug("Downloading dynamic.jsp")

        async with self._session.get(DYNAMIC_URL) as response:
            response.raise_for_status()
            text = await response.text()

        if "login" in text.lower() and "serial" in text.lower():
            if retry:
                _LOGGER.debug("FANN session appears expired, logging in again")
                self._logged_in = False
                await self.login()
                return await self._get_devices_with_retry(retry=False)

            raise FannAuthError("FANN session expired")

        payload = json.loads(text)

        html = payload[0]["data"]
        devices = parse_dynamic(html)

        _LOGGER.debug("Found %d devices", len(devices))

        return devices

    async def wake(self, dbid: int) -> None:
        """Wake device."""
        await self._set_state(dbid, "W")

    async def sleep(self, dbid: int) -> None:
        """Put device to sleep."""
        await self._set_state(dbid, "Z")

    async def _set_state(self, dbid: int, state: str, retry: bool = True) -> None:
        """Set FANN device state."""
        await self.ensure_login()

        async with self._session.get(
            ZZZ_URL,
            params={
                "id": dbid,
                "state": state,
            },
        ) as response:
            response.raise_for_status()
            text = await response.text()

        if "login" in text.lower() and "serial" in text.lower():
            if retry:
                _LOGGER.debug("FANN session expired during command, retrying")
                self._logged_in = False
                await self.login()
                await self._set_state(dbid, state, retry=False)
                return

            raise FannAuthError("FANN session expired during command")