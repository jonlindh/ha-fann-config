"""Switch platform for FANN."""

from __future__ import annotations

import asyncio

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODEL_ECOTREAT
from .entity import FannEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FANN switches."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []

    for dbid, device in coordinator.data.items():
        if device.model == MODEL_ECOTREAT:
            entities.append(FannEkoTreatSwitch(coordinator, dbid))

    async_add_entities(entities)


class FannEkoTreatSwitch(FannEntity, SwitchEntity):
    """FANN EkoTreat switch."""

    _attr_name = None

    def __init__(self, coordinator, dbid: int) -> None:
        """Initialize switch."""
        super().__init__(coordinator, dbid)

        self._attr_unique_id = f"fann_{dbid}_switch"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        device = self.device
        return bool(device and device.is_on)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        device = self.device

        if device is None:
            return {}

        return {
            "dbid": device.dbid,
            "nickname": device.nickname,
            "raw_status": device.raw_status,
            "state": device.state,
            "next_action": device.next_action,
            "people": device.people,
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Wake EkoTreat."""
        await self.coordinator.api.wake(self._dbid)
        await self._poll_until_expected(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Put EkoTreat to sleep."""
        await self.coordinator.api.sleep(self._dbid)
        await self._poll_until_expected(False)

    async def _poll_until_expected(self, expected_on: bool) -> None:
        """Refresh several times after command."""
        for _ in range(12):
            await asyncio.sleep(5)
            await self.coordinator.async_request_refresh()

            device = self.device
            if device and device.is_on == expected_on:
                return