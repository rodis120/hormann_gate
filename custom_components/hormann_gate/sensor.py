"""Sensors for Hormann Gate Integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, TEMP_CELSIUS, PERCENTAGE
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER
from .hub import HormannHub


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entries."""
    name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][name]["hub"]

    sensors = [
        HormannSensor(
            hub,
            "temperature",
            "temperature",
            SensorDeviceClass.TEMPERATURE,
            TEMP_CELSIUS,
        ),
        HormannSensor(
            hub, "humidity", "humidity", SensorDeviceClass.HUMIDITY, PERCENTAGE
        ),
    ]
    async_add_entities(sensors)


class HormannSensor(SensorEntity):
    """Representation of the DHT sensor."""

    def __init__(
        self,
        hub: HormannHub,
        name: str,
        key: str,
        sensor_type: SensorDeviceClass,
        unit: str,
        icon: str = None,
    ) -> None:
        self._hub = hub
        self._name = name
        self._key = key
        if icon:
            self._icon = icon

        self._attr_device_info = {
            "identifiers": {(DOMAIN, hub.name)},
            "name": hub.name,
            "manufacturer": ATTR_MANUFACTURER,
        }

        self._attr_unique_id = f"{hub.name}_{name}"
        self._attr_name = name
        self._attr_device_class = sensor_type
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = unit

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_device(self._data_updated)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callbacks."""
        self._hub.async_remove_device(self._data_updated)

    @callback
    def _data_updated(self) -> None:
        """Handle data update."""
        self._attr_native_value = round(float(self._hub.data[self._key]), 1)
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub."""
        return False

    @property
    def native_value(self):
        return self._attr_native_value
