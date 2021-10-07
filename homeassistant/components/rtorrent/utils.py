import ssl
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
)


class RTorrentUtils:
    @staticmethod
    def _build_url(data):
        user = data[CONF_USERNAME]
        password = data[CONF_PASSWORD]
        host = data[CONF_HOST]
        port = data[CONF_PORT]
        proto = "https" if data[CONF_SSL] else "http"
        if user and password:
            url = f"{proto}://{user}:{password}@{host}:{port}/RPC2"
        else:
            url = f"{proto}://{host}:{port}/RPC2"

        print(url)
        return url

    @staticmethod
    def _is_ssl(data):
        return None if not data[CONF_SSL] else ssl.SSLContext()