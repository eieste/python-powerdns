import json

from powerdns.exceptions import PDNSCanonicalError
from powerdns.interface import PDNSEndpointBase, LOG
from powerdns.models.zone import PDNSZone


class PDNSServer(PDNSEndpointBase):

    def __init__(self, endpoint=None, id="localhost", version=None, daemon_type=None):
        super(PDNSServer, self).__init__(endpoint)
        self._detail = {
            "id": id,
            "version": version,
            "daemon_type": daemon_type,
        }

        self._zone_list = self._load_zone_list()

    def __str__(self):
        return 'PDNSServer:%s' % self.get("id")

    @classmethod
    def parse(cls, endpoint, raw_data):
        return cls(endpoint=endpoint,
                   id=raw_data["id"],
                   version=raw_data["version"],
                   daemon_type=raw_data["daemon_type"])

    def get(self, name):
        return self._detail[name]

    def get_url(self):
        return "/servers/{}".format(self.get("id"))

    def get_zone_url(self):
        return "/servers/{}/zones".format(self.get("id"))

    def _load_zone_list(self):
        return [PDNSZone.parse(self, data) for data in self._get(self.get_zone_url())]

    @property
    def zones(self):
        return self._zone_list

    def get_zone(self, name):
        """
            Get zone by name

            :param str name: Zone name (canonical)
            :return PDNSZone: Zone as :class:`PDNSZone` instance or :obj:`None`
        """
        for zone in self._zone_list:
            if zone.get("name") == name:
                return zone

    def create_zone(self, zone):
        return zone.create(self)