import xmlrpc.client as xmlrpc
import logging
from .errors import AuthenticationError, CannotConnect, UnknownError
from homeassistant.const import STATE_OFF, STATE_ON

_LOGGER = logging.getLogger(__name__)


class TorrentReturn:
    def __init__(self, value=None, available=None):
        self.value = value
        self.available = available


class Torrent:
    def __init__(self, hash, name, status, size, downloaded):
        self.hash = hash
        self.name = name
        self.status = "Started" if status == 1 else "Stopped"
        self.size = self._format_size(size)
        self.downloaded = self._download_percente(size, downloaded)

    def _format_size(self, size):
        return round(size / 1074000000, 2)

    def _download_percente(self, size, downloaded):
        return round(((100 * downloaded) / size), 2)


class RTorrentClient:
    def __init__(self, url, ssl=None):
        self.url = url
        self.ssl_context = ssl
        self.connexion = self._check_conn(self._get_xmlrpc_conn())
        self.available: bool = True

        # assert (
        #    self._check_conn(self._get_xmlrpc_conn()) is True
        # ), "rTorrent connection failed ici"

    def _check_conn(self, conn):
        """Verify given ServerProxy connection is to an rTorrent XMLRPC server"""
        try:
            _rpc_methods = conn.system.listMethods()
        except (OSError, ConnectionRefusedError, xmlrpc.Fault, Exception) as error:
            _LOGGER.error("*** Exception caught: Connexion Faillure")
            raise CannotConnect from error

        # simple check, probably sufficient
        if (
            "system.client_version" not in _rpc_methods
            or "system.library_version" not in _rpc_methods
        ):
            return False
        else:
            return True

    def _get_xmlrpc_conn(self):
        """Get ServerProxy instance"""
        return xmlrpc.ServerProxy(self.url, context=self.ssl_context)

    def _get_all_torrent(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2(
                "",
                "main",
                "d.hash=",
                "d.name=",
                "d.is_active=",
                "d.size_bytes=",
                "d.completed_bytes=",
            )
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        torrents = []
        for entry in data:
            torrent = Torrent(
                entry.__getitem__(0),
                entry.__getitem__(1),
                entry.__getitem__(2),
                entry.__getitem__(3),
                entry.__getitem__(4),
            )
            torrents.append(torrent)
        return torrents

    def _get_global_speed_upload(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.throttle.global_up.rate()
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return data

    def _get_global_speed_download(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.throttle.global_down.rate()
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return data

    def _get_stopped_torrent(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "stopped")
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return len(data)

    def _get_completed_torrent(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "complete")
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return len(data)

    def _get_uploading_torrents(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "seeding", "d.up.rate=")
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return len(data)

    def _get_downloading_torrents(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "leeching", "d.down.rate=")
            data = call()[0]
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            return
        return len(data)

    def turn_on(self):
        """Turn the device on."""
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "started", "d.resume=")
            call()[0]
            self.available = True
        except (xmlrpc.ProtocolError, ConnectionRefusedError):
            _LOGGER.error("Connection to rtorrent")
            self.available = False

    def turn_off(self):
        """Turn the device off."""
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "started", "d.pause=")
            call()[0]
            self.available = True
        except (xmlrpc.ProtocolError, ConnectionRefusedError, xmlrpc.Fault):
            _LOGGER.error("Error calling method")
            self.available = False

    def is_active_torrent(self):
        try:
            call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
            call.d.multicall2("", "started", "d.is_active=")
            data = call()[0]
            self.available = True
        except (xmlrpc.ProtocolError, ConnectionRefusedError, OSError) as ex:
            _LOGGER.error("Connection to rtorrent failed (%s)", ex)
            self.available = False
        for torrent in data:
            if torrent[0] == 1:
                return STATE_ON
        return STATE_OFF

    def _request(self, *args):
        call = xmlrpc.MultiCall(self._get_xmlrpc_conn())
        call.d.multicall2(args)
        data = call()
        return data[0]
