"""Diagnostics support for FANN."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict:
    """Return diagnostics for a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    devices = []

    for device in coordinator.data.values():
        devices.append(
            {
                "dbid": device.dbid,
                "nickname": device.nickname,
                "model": device.model,
                "connected": device.connected,
                "is_on": device.is_on,
                "state": device.state,
                "raw_status": device.raw_status,
                "next_action": device.next_action,
                "people": device.people,
                "schedule": device.schedule,
            }
        )

    return {
        "entry_title": entry.title,
        "device_count": len(devices),
        "devices": devices,
    }