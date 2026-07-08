"""Data coordinator for FANN."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Callable

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FannApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FannDataUpdateCoordinator(DataUpdateCoordinator):
    """FANN data update coordinator."""

    def __init__(self, hass, api: FannApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from FANN."""
        _LOGGER.debug("Updating FANN data")

        devices = await self.api.get_devices()

        _LOGGER.debug("Updated FANN data: %d devices", len(devices))

        return {device.dbid: device for device in devices}

    def get_device(self, dbid: int):
        if not self.data:
            return None
        return self.data.get(dbid)

    async def refresh_until(
        self,
        dbid: int,
        condition: Callable[[object], bool],
        timeout: int = 60,
        interval: int = 5,
    ) -> None:
        """Refresh until condition is true or timeout expires."""

        for _ in range(timeout // interval):
            await asyncio.sleep(interval)
            await self.async_request_refresh()

            device = self.get_device(dbid)
            if device and condition(device):
                _LOGGER.debug("FANN device %s reached expected state: %s", dbid, device.state)
                return

        _LOGGER.debug("Timed out waiting for FANN device %s to reach expected state", dbid)