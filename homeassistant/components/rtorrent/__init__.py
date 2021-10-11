"""The Rtorrent integration."""
from __future__ import annotations

import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from .client import RTorrentClient
from .utils import RTorrentUtils
import xmlrpc.client as xmlrpc
from .const import DOMAIN, PLATFORMS, SERVICE_ADD_TORRENT_SCHEMA
from homeassistant.helpers.typing import ConfigType

LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Hello World component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up torrent from a config entry."""

    try:
        client = await hass.async_add_executor_job(
            RTorrentClient,
            RTorrentUtils._build_url(entry.data),
            RTorrentUtils._is_ssl(entry.data),
        )
    except (OSError, ConnectionRefusedError, xmlrpc.Fault, Exception):
        LOGGER.error("*** Exception caught: Connexion Faillure")
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    def add_torrent(service: ServiceCall) -> None:
        """Add new torrent to download."""
        r_client = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data["name"] == service.data["name"]:
                r_client = hass.data[DOMAIN][entry.entry_id]
                break
        if r_client is None:
            LOGGER.error("Transmission instance is not found")
            return
        torrent = service.data["rtorrent"]
        if torrent.startswith(
            ("http", "ftp:", "magnet:")
        ) or hass.config.is_allowed_path(torrent):
            r_client.add_torrent(torrent)
        else:
            LOGGER.warning("Could not add torrent: unsupported type or no permission")

    hass.services.register(
        DOMAIN, "add_torrent", add_torrent, SERVICE_ADD_TORRENT_SCHEMA
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
