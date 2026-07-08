"""Sensor platform for FANN."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
        entities.append(FannStatusSensor(coordinator, dbid))

        if device.model == MODEL_ECOTREAT:
            entities.append(FannPeopleSensor(coordinator, dbid))

        if device.model == MODEL_BIOBED:
            entities.append(FannScheduleSensor(coordinator, dbid))

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
        return self.device.status_display if self.device else None

    @property
    def extra_state_attributes(self):
        device = self.device
        if device is None:
            return {}
        return {
            "raw_status": device.raw_status,
            "state": device.state,
            "transition": device.transition,
        }


class FannPeopleSensor(FannEntity, SensorEntity):
    _attr_name = "People"
    _attr_icon = "mdi:account-group"

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_people"

    @property
    def native_value(self):
        return self.device.people if self.device else None


class FannScheduleSensor(FannEntity, SensorEntity):
    _attr_name = "Schedule"
    _attr_icon = "mdi:calendar-clock"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_schedule"

    @property
    def native_value(self):
        return self.device.schedule if self.device else None