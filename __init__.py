"""The Hormann Gate integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_NAME, CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import HormannHub

PLATFORMS: list[Platform] = [Platform.COVER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hormann Gate from a config entry."""

    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][name] = {"hub": HormannHub(name, host, hass)}

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.data[CONF_NAME])

    return unload_ok
