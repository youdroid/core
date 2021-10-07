"""Support for monitoring the rtorrent BitTorrent client API."""
import logging
import xmlrpc.client

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import DATA_RATE_KILOBYTES_PER_SECOND, STATE_IDLE
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_CURRENT_STATUS = "current_status"
SENSOR_TYPE_DOWNLOAD_SPEED = "download_speed"
SENSOR_TYPE_UPLOAD_SPEED = "upload_speed"
SENSOR_TYPE_ALL_TORRENTS = "all_torrents"
SENSOR_TYPE_STOPPED_TORRENTS = "stopped_torrents"
SENSOR_TYPE_COMPLETE_TORRENTS = "complete_torrents"
SENSOR_TYPE_UPLOADING_TORRENTS = "uploading_torrents"
SENSOR_TYPE_DOWNLOADING_TORRENTS = "downloading_torrents"
SENSOR_TYPE_ACTIVE_TORRENTS = "active_torrents"

from .const import DOMAIN, STATE_TORRENT


SENSOR_TYPES = {
    SENSOR_TYPE_CURRENT_STATUS: ["Status", None],
    SENSOR_TYPE_DOWNLOAD_SPEED: ["Down Speed", DATA_RATE_KILOBYTES_PER_SECOND],
    SENSOR_TYPE_UPLOAD_SPEED: ["Up Speed", DATA_RATE_KILOBYTES_PER_SECOND],
    SENSOR_TYPE_ALL_TORRENTS: ["All Torrents", STATE_TORRENT],
    SENSOR_TYPE_STOPPED_TORRENTS: ["Stopped Torrents", STATE_TORRENT],
    SENSOR_TYPE_COMPLETE_TORRENTS: ["Complete Torrents", STATE_TORRENT],
    SENSOR_TYPE_UPLOADING_TORRENTS: ["Uploading Torrents", STATE_TORRENT],
    SENSOR_TYPE_DOWNLOADING_TORRENTS: ["Downloading Torrents", STATE_TORRENT],
    SENSOR_TYPE_ACTIVE_TORRENTS: ["Active Torrents", STATE_TORRENT],
}


async def async_setup_entry(hass, config_entry, async_add_entities):

    rt_client = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        RTorrentSpeedSensor(SENSOR_TYPE_DOWNLOAD_SPEED, rt_client),
        RTorrentSpeedSensor(SENSOR_TYPE_UPLOAD_SPEED, rt_client),
        RTorrentSpeedStatus(SENSOR_TYPE_CURRENT_STATUS, rt_client),
        RTorrentTorrentSensor(SENSOR_TYPE_STOPPED_TORRENTS, rt_client),
        RTorrentTorrentSensor(SENSOR_TYPE_COMPLETE_TORRENTS, rt_client),
        RTorrentTorrentSensor(SENSOR_TYPE_UPLOADING_TORRENTS, rt_client),
        RTorrentTorrentSensor(SENSOR_TYPE_DOWNLOADING_TORRENTS, rt_client),
        RTorrentTorrentSensor(SENSOR_TYPE_ACTIVE_TORRENTS, rt_client),
    ]
    async_add_entities(sensors, True)


class RTorrentSensor(SensorEntity):
    """Representation of an rtorrent sensor."""

    def __init__(self, sensor_type, rtorrent_client):
        """Initialize the sensor."""
        self._name = SENSOR_TYPES[sensor_type][0]
        self.client = rtorrent_client
        self.type = sensor_type
        self.client_name = DOMAIN
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self.data = None
        self._available = True

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name} {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement


class RTorrentSpeedSensor(RTorrentSensor):
    def update(self):
        """Get the latest data from Transmission and updates the state."""
        if self._name == "Down Speed":
            data = self.client._get_global_speed_download()
        else:
            data = self.client._get_global_speed_upload()
        self._state = data


class RTorrentSpeedStatus(RTorrentSensor):
    def update(self):
        upload = self.client._get_global_speed_upload()
        download = self.client._get_global_speed_download()
        if upload > 0 and download > 0:
            self._state = "up_down"
        elif upload > 0 and download == 0:
            self._state = "seeding"
        elif upload == 0 and download > 0:
            self._state = "downloading"
        else:
            self._state = STATE_IDLE


class RTorrentTorrentSensor(RTorrentSensor):
    def update(self):
        if self._name == "Stopped Torrents":
            self._state = self.client._get_stopped_torrent()
        elif self._name == "Complete Torrents":
            self._state = self.client._get_completed_torrent()
        elif self._name == "Uploading Torrents":
            self._state = self.client._get_uploading_torrents()
        elif self._name == "Downloading Torrents":
            self._state = self.client._get_downloading_torrents()
        elif self._name == "Active Torrents":
            self._state = (
                self.client._get_uploading_torrents()
                + self.client._get_downloading_torrents()
            )
