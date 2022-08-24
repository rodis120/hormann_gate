"""Hormann hub."""
from typing import Optional
from datetime import timedelta
import requests
from requests.exceptions import JSONDecodeError, ConnectTimeout

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval

from .const import UPDATE_INTERVAL


class HormannHub:
    """Hormann hub."""

    def __init__(self, name: str, host: str, hass: HomeAssistant) -> None:
        self._name = name
        self._host = host
        self._hass = hass
        self._devices = []
        self._unsub_interval_method = async_track_time_interval(
            self._hass, self._update_data, timedelta(seconds=UPDATE_INTERVAL)
        )

        self.data = {}

    @property
    def name(self) -> str:
        """Returns the name of the hormann integration."""
        return self._name

    async def update(self) -> None:
        """Manual update."""
        await self._update_data()

    @callback
    def async_add_device(self, update_callback) -> None:
        """Add device to update list."""
        self._devices.append(update_callback)

    @callback
    def async_remove_device(self, update_callback) -> None:
        """Remove device from update list."""
        self._devices.remove(update_callback)

        if not self._devices:
            self._unsub_interval_method()
            self._unsub_interval_method = None

    async def _update_data(self, _now: Optional[int] = None) -> None:

        try:
            await self._hass.async_add_executor_job(self._read_data_from_device)
        except (ConnectTimeout, ConnectionError, JSONDecodeError):
            return

        for update_callback in self._devices:
            update_callback()

    def _read_data_from_device(self):

        resp = requests.get(f"http://{self._host}/status")
        if resp.status_code != 200:
            raise Exception

        resp = resp.json()

        self.data["lamp"] = resp["lamp"]
        self.data["position"] = resp["doorposition"]
        self.data["doorstate"] = resp["doorstate"]

        resp = requests.get(f"http://{self._host}/dht")
        if resp.status_code != 200:
            raise Exception

        resp = resp.json()

        self.data["temperature"] = resp["temperature"]
        self.data["humidity"] = resp["humidity"]

    def _send_command(self, cmd: int) -> bool:

        resp = requests.get(f"http://{self._host}/command", {"action": cmd})
        return True if resp.content.decode("utf-8") == "OK" else False

    def close_gate(self) -> None:
        "Close the gate."
        self._send_command(0)

    def open_gate(self) -> None:
        "Open the gate."
        self._send_command(1)

    def stop_gate(self) -> None:
        "Open the gate."
        self._send_command(2)
