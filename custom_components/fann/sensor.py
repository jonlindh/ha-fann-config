"""Sensor platform for FANN."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODEL_ECOTREAT
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
        if device.model == MODEL_ECOTREAT:
            entities.append(FannStatusSensor(coordinator, dbid))
            entities.append(FannPeopleSensor(coordinator, dbid))

    async_add_entities(entities)


class FannStatusSensor(FannEntity, SensorEntity):
    _attr_name = "Status"
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_status"

    @property
    def native_value(self):
        return self.device.raw_status if self.device else None


class FannPeopleSensor(FannEntity, SensorEntity):
    _attr_name = "People"
    _attr_icon = "mdi:account-group"

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_people"

    @property
    def native_value(self):
        return self.device.people if self.device else None