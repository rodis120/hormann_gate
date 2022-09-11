"""Cover for Hormann Gate integration."""
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOT_TOPIC, DOMAIN, ATTR_MANUFACTURER


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup cover entries."""
    name = entry.data[CONF_NAME]
    root_topic = entry.data[CONF_ROOT_TOPIC]

    async_add_entities([HormannCover(hass, root_topic, name)])


class HormannCover(CoverEntity):
    """Representation of hormann cover."""

    def __init__(self, hass: HomeAssistant, root_topic: str, name: str) -> None:
        self._hass = hass
        self._root_topic = root_topic
        self._name = name

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{name}_{root_topic}")},
            "name": name,
            "manufacturer": ATTR_MANUFACTURER,
        }

        self._attr_name = name
        self._attr_unique_id = f"{name}_{root_topic}_cover"
        self._attr_device_class = CoverDeviceClass.GARAGE
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

        self._attr_is_closed = False
        self._attr_is_closing = False
        self._attr_is_opening = False

    async def async_added_to_hass(self) -> None:
        """Subscribe topics."""
        await mqtt.async_subscribe(
            self._hass, f"{self._root_topic}/position", self.position_updated, 0
        )
        await mqtt.async_subscribe(
            self._hass, f"{self._root_topic}/doorstate", self.state_updated, 0
        )

    @callback
    async def position_updated(self, msg: ReceiveMessage) -> None:
        """Handle position update."""

        self._attr_current_cover_position = int(msg.payload) / 2
        self.async_write_ha_state()

    @callback
    async def state_updated(self, msg: ReceiveMessage) -> None:
        """Handle state update."""

        state = int(msg.payload)

        self._attr_is_closed = state == 64
        self._attr_is_closing = state == 2
        self._attr_is_opening = state == 1

        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open gate."""
        await mqtt.async_publish(self._hass, f"{self._root_topic}/action", "open", 0)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close gate."""
        await mqtt.async_publish(self._hass, f"{self._root_topic}/action", "close", 0)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop gate."""
        await mqtt.async_publish(self._hass, f"{self._root_topic}/action", "stop", 0)
