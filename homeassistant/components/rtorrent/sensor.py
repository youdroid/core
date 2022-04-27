"""Platform for sensor integration."""
import logging

from homeassistant.components.sensor import SensorEntity

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_IDLE

from .const import (
    DOMAIN,
    SENSOR_TYPE_CURRENT_STATUS,
    SENSOR_TYPE_DOWNLOAD_SPEED,
    SENSOR_TYPE_UPLOAD_SPEED,
    SENSOR_TYPE_STOPPED_TORRENTS,
    SENSOR_TYPE_COMPLETE_TORRENTS,
    SENSOR_TYPE_UPLOADING_TORRENTS,
    SENSOR_TYPE_DOWNLOADING_TORRENTS,
    SENSOR_TYPE_ACTIVE_TORRENTS,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
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
    async_add_entities(sensors)


class RTorrentSensor(SensorEntity):
    """Representation of an Generic rtorrent sensor."""

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

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self._name}_sensor"


class RTorrentSpeedSensor(RTorrentSensor):
    """Representation of an speed rtorrent sensor."""

    def update(self):
        """Get the latest data from Rtorrent and updates the state."""
        if self._name == "Down Speed":
            data = self.client._get_global_speed_download()
        else:
            data = self.client._get_global_speed_upload()
        self._state = data

    @property
    def icon(self):
        """Icon of the entity."""
        return "mdi:speedometer"


class RTorrentSpeedStatus(RTorrentSensor):
    """Representation of an speed rtorrent sensor."""

    def update(self):
        """Get the latest data from Rtorrent and updates the state."""
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
    """Representation of an extra rtorrent sensor."""

    def update(self):
        """Get the latest data from Rtorrent and updates the state."""
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
