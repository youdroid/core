"""Constants for the Rtorrent integration."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "rtorrent"
STATE_TORRENT = "torrents"
PLATFORMS: list[str] = ["sensor", "switch"]
SERVICE_ADD_TORRENT_SCHEMA = vol.Schema(
    {vol.Required("torrent"): cv.string, vol.Required("name"): cv.string}
)
