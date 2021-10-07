"""Support for monitoring the rtorrent BitTorrent client API."""
import logging
import xmlrpc.client

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_URL, STATE_OFF, STATE_ON
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the rtorrent switch."""
    rt_client = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([RTorrentSwitch(rt_client, DOMAIN)])


class RTorrentSwitch(ToggleEntity):
    """Representation of a rtorrent switch."""

    def __init__(self, rt_client, name):
        """Initialize the Deluge switch."""
        self._name = name
        self.rt_client = rt_client
        self._state = STATE_OFF

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    @property
    def available(self):
        """Return true if device is available."""
        return self.rt_client.available

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.rt_client.turn_on()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.rt_client.turn_off()

    def update(self):
        """Get the latest data from rtorrent and updates the state."""
        self._state = self.rt_client.is_active_torrent()