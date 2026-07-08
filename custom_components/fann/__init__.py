"""FANN Config integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import FannApi
from .const import CONF_KEY, CONF_SERIAL, DOMAIN, PLATFORMS
from .coordinator import FannDataUpdateCoordinator


async def async_setup(hass: HomeAssistant, config):
    """Set up FANN from YAML."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up FANN from a config entry."""

    api = FannApi(
        serial=entry.data[CONF_SERIAL],
        key=entry.data[CONF_KEY],
    )

    coordinator = FannDataUpdateCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].disconnect()

    return unload_ok