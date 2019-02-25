from powerdns.interface import PDNSEndpointBase, LOG
from powerdns.models.server import PDNSServer


class PDNSEndpoint(PDNSEndpointBase):
    """PowerDNS API Endpoint

    :param PDNSApiClient api_client: Cachet API client instance

    The :class:`~PDNSEndpoint` class defines the following attributes:

    .. autoattribute:: servers

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#api-spec
    """
    def __init__(self, api_client):
        """Initialization method"""
        self._api_client = api_client
        super(PDNSEndpoint, self).__init__(self)
        self._servers = None
        self._server_list = None
        if not self._servers:
            self._server_list = self._load_server_list()

    def __repr__(self):
        return 'PDNSEndpoint(%s)' % self.api_client

    def __str__(self):
        return 'PDNSEndpoint:%s' % self.api_client.api_endpoint

    def _load_server_list(self):
        """
            Requests the PDNS Admin API and return a Server List
            :return PDNSServer List: list of all PDNSServers on this endpoint
        """
        return [PDNSServer.parse(self, data) for data in self._get('/servers')]

    def get_server(self, id):
        """
            Returns server by name
            :param sid: Id of Server to use
            :return PDNSServer: :class: `PDNSServer` Instance
        """
        for server in self._server_list:
            if server.get("id") == id:
                return server