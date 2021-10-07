"""The torrent integration."""
from __future__ import annotations

import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .client import RTorrentClient
from .utils import RTorrentUtils
import xmlrpc.client as xmlrpc
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = ["sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up torrent from a config entry."""

    try:
        client = await hass.async_add_executor_job(
            RTorrentClient,
            RTorrentUtils._build_url(entry.data),
            RTorrentUtils._is_ssl(entry.data),
        )
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
    except (OSError, ConnectionRefusedError, xmlrpc.Fault, Exception):
        _LOGGER.error("*** Exception caught: Connexion Faillure")
        return False

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
