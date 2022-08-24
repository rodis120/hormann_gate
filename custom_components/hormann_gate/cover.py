"""Cover for Hormann Gate integration."""
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER
from .hub import HormannHub


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entries."""
    name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][name]["hub"]

    async_add_entities([HormannCover(hub, name)])


class HormannCover(CoverEntity):
    """Representation of hormann cover."""

    def __init__(self, hub: HormannHub, name: str) -> None:
        self._hub = hub
        self._name = name

        self._attr_device_info = {
            "identifiers": {(DOMAIN, hub.name)},
            "name": hub.name,
            "manufacturer": ATTR_MANUFACTURER,
        }

        self._attr_name = name
        self._attr_unique_id = f"{hub.name}_{name}"
        self._attr_device_class = CoverDeviceClass.GARAGE
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

        self._attr_is_closed = False
        self._attr_is_closing = False
        self._attr_is_opening = False

    async def async_update(self) -> None:
        """Update state"""
        await self._hub.update()

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_device(self._data_updated)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callbacks."""
        self._hub.async_remove_device(self._data_updated)

    @callback
    def _data_updated(self) -> None:
        """Handle data update."""

        state = self._hub.data["doorstate"]

        self._attr_is_closed = state == 64
        self._attr_is_closing = state == 2
        self._attr_is_opening = state == 1

        pos = self._hub.data["position"]
        self._attr_current_cover_position = pos

        self.async_write_ha_state()

    def open_cover(self, **kwargs: Any) -> None:
        """Open gate."""
        self._hub.open_gate()

    def close_cover(self, **kwargs: Any) -> None:
        """Close gate."""
        self._hub.close_gate()

    def stop_cover(self, **kwargs: Any) -> None:
        self._hub.stop_gate()
