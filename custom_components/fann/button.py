"""Button platform for FANN."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import FannEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FANN buttons."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        FannRefreshButton(coordinator, dbid)
        for dbid in coordinator.data
    ]

    async_add_entities(entities)


class FannRefreshButton(FannEntity, ButtonEntity):
    """Refresh FANN device."""

    _attr_name = "Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator, dbid: int) -> None:
        """Initialize button."""
        super().__init__(coordinator, dbid)
        self._attr_unique_id = f"fann_{dbid}_refresh"

    async def async_press(self) -> None:
        """Refresh FANN data immediately."""
        await self.coordinator.async_request_refresh()