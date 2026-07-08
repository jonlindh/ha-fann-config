"""Binary sensor platform for FANN."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import FannEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        FannConnectedBinarySensor(coordinator, dbid)
        for dbid in coordinator.data
    ]

    async_add_entities(entities)


class FannConnectedBinarySensor(FannEntity, BinarySensorEntity):
    _attr_name = "Connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_connected"

    @property
    def is_on(self) -> bool:
        return bool(self.device and self.device.connected)