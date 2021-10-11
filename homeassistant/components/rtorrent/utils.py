"""Helper for the Rtorrent integration."""
import ssl

# from lib import bencodepy

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
)


class RTorrentUtils:
    """Util class."""

    @staticmethod
    def _build_url(data):
        """Generate URL."""
        user = data[CONF_USERNAME]
        password = data[CONF_PASSWORD]
        host = data[CONF_HOST]
        port = data[CONF_PORT]
        proto = "https" if data[CONF_SSL] else "http"
        if user and password:
            url = f"{proto}://{user}:{password}@{host}:{port}/RPC2"
        else:
            url = f"{proto}://{host}:{port}/RPC2"
        return url

    @staticmethod
    def _is_ssl(data):
        """Enable ssl."""
        return None if not data[CONF_SSL] else ssl.SSLContext()

    # @staticmethod
    # def get_hash(torrent, file_bytes=False):
    #     """Gets hash from torrent or magnet
    #     torrent (str): torrent/magnet url or bytestring of torrent file contents
    #     file_bytes (bool): if url is bytes of torrent file
    #     If file_bytes == True, torrent should be a bytestring of the contents of the torrent file
    #     Returns str of lower-case torrent hash or '' if exception
    #     """

    #     if not file_bytes and torrent.startswith("magnet"):
    #         return torrent.split("&")[0].split(":")[-1].upper()
    #     else:
    #         try:
    #             raw = torrent if file_bytes else Url.open(torrent, stream=True).content
    #             metadata = bencodepy.decode(raw)
    #             hashcontents = bencodepy.encode(metadata[b"info"])
    #             return hashlib.sha1(hashcontents).hexdigest().upper()
    #         except Exception as e:
    #             logging.error("Unable to get torrent hash", exc_info=True)
    #             return ""
