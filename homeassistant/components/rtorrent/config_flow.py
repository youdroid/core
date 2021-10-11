"""Config flow for torrent integration."""
import logging
from typing import Any
import ssl
import voluptuous as vol
from .client import RTorrentClient
from .utils import RTorrentUtils

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
)
from .const import DOMAIN
from .errors import AuthenticationError, CannotConnect

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Required(CONF_PORT): int,
        vol.Optional(CONF_SSL, default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    user = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]
    proto = "https" if data[CONF_SSL] else "http"

    if user and password:
        url = "{}://{}:{}@{}:{}/RPC2".format(
            proto, user, password, data[CONF_HOST], data[CONF_PORT]
        )
    else:
        url = "{}://{}:{}/RPC2".format(proto, data[CONF_HOST], data[CONF_PORT])

    context = None if data[CONF_SSL] else ssl.SSLContext()
    try:
        await hass.async_add_executor_job(RTorrentClient, url, context)
    except (OSError) as error:
        logging.error("Torrent connection test failed.", exc_info=True)
        raise CannotConnect from error


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for torrent."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        errors = {}

        try:

            await validate_input(self.hass, user_input)

            await self.hass.async_add_executor_job(
                RTorrentClient,
                RTorrentUtils._build_url(user_input),
                RTorrentUtils._is_ssl(user_input),
            )

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except AuthenticationError:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=DOMAIN, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
