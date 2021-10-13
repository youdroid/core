"""Constants for the Rtorrent integration."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
    DATA_RATE_KILOBYTES_PER_SECOND,
)

DOMAIN = "rtorrent"
STATE_TORRENT = "torrents"
PLATFORMS: list[str] = ["sensor", "switch"]

SERVICE_ADD_TORRENT_SCHEMA = vol.Schema(
    {vol.Required("torrent"): cv.string, vol.Required("name"): cv.string}
)

SERVICE_REMOVE_TORRENT_SCHEMA = vol.Schema({vol.Required("torrent"): cv.string})

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Required(CONF_PORT): int,
        vol.Optional(CONF_SSL, default=False): bool,
    }
)

SENSOR_TYPE_CURRENT_STATUS = "current_status"
SENSOR_TYPE_DOWNLOAD_SPEED = "download_speed"
SENSOR_TYPE_UPLOAD_SPEED = "upload_speed"
SENSOR_TYPE_ALL_TORRENTS = "all_torrents"
SENSOR_TYPE_STOPPED_TORRENTS = "stopped_torrents"
SENSOR_TYPE_COMPLETE_TORRENTS = "complete_torrents"
SENSOR_TYPE_UPLOADING_TORRENTS = "uploading_torrents"
SENSOR_TYPE_DOWNLOADING_TORRENTS = "downloading_torrents"
SENSOR_TYPE_ACTIVE_TORRENTS = "active_torrents"


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
