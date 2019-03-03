from powerdns.interface import PDNSEndpointBase, LOG
from powerdns.models.server import PDNSServer


class PDNSEndpoint(PDNSEndpointBase):

    def __init__(self, api_client):
        """Initialization method"""
        super(PDNSEndpoint, self).__init__(api_client)
        self._server_list = self._load_server_list()

    def __repr__(self):
        return 'PDNSEndpoint(%s)' % self.get_api_client()

    def __str__(self):
        return 'PDNSEndpoint:%s' % self.get_api_client()

    def get_api_client(self):
        return self._parent

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