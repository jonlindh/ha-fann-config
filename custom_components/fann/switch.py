"""Switch platform for FANN."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODEL_BIOBED, MODEL_ECOTREAT
from .entity import FannEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []

    for dbid, device in coordinator.data.items():
        if device.model in [MODEL_ECOTREAT, MODEL_BIOBED]:
            entities.append(FannDeviceSwitch(coordinator, dbid))

    async_add_entities(entities)


class FannDeviceSwitch(FannEntity, SwitchEntity):
    """FANN device switch."""

    _attr_name = "Power"
    _attr_has_entity_name = True
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_switch"

    @property
    def is_on(self) -> bool:
        device = self.device
        return bool(device and device.is_on)

    @property
    def extra_state_attributes(self) -> dict:
        device = self.device

        if device is None:
            return {}

        return {
            "dbid": device.dbid,
            "nickname": device.nickname,
            "model": device.model,
            "connected": device.connected,
            "raw_status": device.raw_status,
            "state": device.state,
            "next_action": device.next_action,
            "people": device.people,
            "schedule": device.schedule,
        }

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.wake(self._dbid)

        await self.coordinator.async_request_refresh()

        await self.coordinator.refresh_until(
            self._dbid,
            lambda device: device.is_on,
            interval=2,
            timeout=60,
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.sleep(self._dbid)

        await self.coordinator.async_request_refresh()

        await self.coordinator.refresh_until(
            self._dbid,
            lambda device: not device.is_on,
            interval=2,
            timeout=60,
        )