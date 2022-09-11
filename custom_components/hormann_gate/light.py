"""Cover for Hormann Gate integration."""
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_ROOT_TOPIC


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup light entries."""
    name = entry.data[CONF_NAME]
    root_topic = entry.data[CONF_ROOT_TOPIC]

    async_add_entities([HormannLight(hass, root_topic, name)])


class HormannLight(LightEntity):
    """Representation of hormann light."""

    def __init__(self, hass: HomeAssistant, root_topic: str, name: str) -> None:

        self._hass = hass
        self._root_topic = root_topic
        self._name = name

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{name}_{root_topic}")},
            "name": name,
            "manufacturer": ATTR_MANUFACTURER,
        }

        self._attr_unique_id = f"{name}_{root_topic}_light"
        self._attr_name = name
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = [ColorMode.ONOFF]

    async def async_added_to_hass(self) -> None:
        """Subscribe topics."""
        await mqtt.async_subscribe(
            self._hass, f"{self._root_topic}/light", self.state_updated, 0
        )

    @callback
    async def state_updated(self, msg: ReceiveMessage) -> None:
        """Handle state update."""
        if not msg.payload.lower() in ["true", "false"]:
            return

        self._attr_is_on = msg.payload.lower() == "true"
        self._async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await mqtt.async_publish(self._hass, f"{self._root_topic}/light", "true", 0)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await mqtt.async_publish(self._hass, f"{self._root_topic}/light", "false", 0)
