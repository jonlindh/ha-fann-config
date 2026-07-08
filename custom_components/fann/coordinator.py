"""Data coordinator for FANN."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FannApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FannDataUpdateCoordinator(DataUpdateCoordinator):
    """FANN data update coordinator."""

    def __init__(self, hass, api: FannApi) -> None:
        """Initialize coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

        self.api = api

    async def _async_update_data(self):
        """Fetch data from FANN."""

        devices = await self.api.get_devices()

        return {
            device.dbid: device
            for device in devices
        }

    def get_device(self, dbid: int):
        """Get device by dbid."""

        return self.data.get(dbid)