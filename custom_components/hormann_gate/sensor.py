"""Sensors for Hormann Gate Integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, TEMP_CELSIUS, PERCENTAGE
from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_ROOT_TOPIC


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entries."""
    device_name = entry.data[CONF_NAME]
    root_topic = entry.data[CONF_ROOT_TOPIC]

    sensors = [
        HormannSensor(
            hass,
            root_topic,
            "sensor/temperature",
            device_name,
            "temperature",
            SensorDeviceClass.TEMPERATURE,
            TEMP_CELSIUS,
        ),
        HormannSensor(
            hass,
            root_topic,
            "sensor/humidity",
            device_name,
            "humidity",
            SensorDeviceClass.HUMIDITY,
            PERCENTAGE,
        ),
    ]
    async_add_entities(sensors)


class HormannSensor(SensorEntity):
    """Representation of the DHT sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        root_topic: str,
        topic: str,
        device_name: str,
        sensor_name: str,
        sensor_type: SensorDeviceClass,
        unit: str,
        icon: str = None,
    ) -> None:

        self._hass = hass
        self._root_topic = root_topic
        self._topic = topic

        if icon:
            self._icon = icon

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{device_name}_{root_topic}")},
            "name": device_name,
            "manufacturer": ATTR_MANUFACTURER,
        }

        self._attr_unique_id = f"{device_name}_{root_topic}_{sensor_name}"
        self._attr_name = sensor_name
        self._attr_device_class = sensor_type
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = unit

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await mqtt.async_subscribe(
            self._hass, f"{self._root_topic}/{self._topic}", self.data_updated, 0
        )

    @callback
    async def data_updated(self, msg: ReceiveMessage) -> None:
        """Handle data update."""
        self._attr_native_value = round(float(msg.payload), 1)
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub."""
        return False

    @property
    def native_value(self):
        return self._attr_native_value
