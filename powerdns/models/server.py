import json

from powerdns.exceptions import PDNSCanonicalError
from powerdns.interface import PDNSEndpointBase, LOG
from powerdns.models.zone import PDNSZone


class PDNSServer(PDNSEndpointBase):
    """Powerdns API Server Endpoint

    :param PDNSApiClient api_client: Cachet API client instance
    :param str api_data: PowerDNS API server data

    api_data structure is received from API, here an example structure::

        {
          "type": "Server",
          "id": "localhost",
          "url": "/api/v1/servers/localhost",
          "daemon_type": "recursor",
          "version": "VERSION",
          "config_url": "/api/v1/servers/localhost/config{/config_setting}",
          "zones_url": "/api/v1/servers/localhost/zones{/zone}",
        }

    The :class:`~PDNSServer` class defines the following attributes:

    .. autoattribute:: config
    .. autoattribute:: zones

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#servers
    """
    def __init__(self, endpoint, id="localhost", version=None, daemon_type=None):
        """
            Creates a new PDNSServer Object; Receive attributes from API

            :param endpoint: PDNSEndpoint Object
            :param sid: The id of the server, “localhost”
            :param version: The version of the server software
            :param daemon_type: “recursor” for the PowerDNS Recursor and “authoritative” for the Authoritative Server
        """

        self._endpoint = endpoint
        super(PDNSServer, self).__init__(endpoint)

        self._details = {
            "id": id,
            "version": version,
            "daemon_type": daemon_type,
        }

        self._zone_list = []

        if len(self._zone_list) <= 0:
            self._zone_list = self._load_zone_list()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'PDNSServer:%s' % self.id

    def get_parent(self):
        return self._endpoint

    def get(self, name):
        return self._details[name]

    def set(self, name, value):
        self._details[name] = value

    @classmethod
    def parse(cls, endpoint, raw_data):
        return cls(endpoint=endpoint,
                   id=raw_data["id"],
                   version=raw_data["version"],
                   daemon_type=raw_data["daemon_type"])

    def get_url(self):
        return "/servers/{}".format(self.get("id"))

    def get_config_url(self):
        return "/servers/{}/config".format(self.get("id"))

    def get_zone_url(self):
        return "/servers/{}/zones".format(self.get("id"))

    def _load_zone_list(self):
        return [PDNSZone.parse(self, data) for data in self._get(self.get_zone_url())]

    def get_zone_list(self):
        return self._zone_list

    def search(self, search_term, max_result=100):
        """Search term using API search endpoint

        :param str search_term:
        :param int max_result:
        :return: Query results as :func:`list`

        API response is a list of one or more of the following objects:

        For a zone::

            {
              "name": "<zonename>",
              "object_type": "zone",
              "zone_id": "<zoneid>"
            }

        For a record::

            {
              "content": "<content>",
              "disabled": <bool>,
              "name": "<name>",
              "object_type": "record",
              "ttl": <ttl>,
              "type": "<type>",
              "zone": "<zonename>,
              "zone_id": "<zoneid>"
            }

        For a comment::

            {
              "object_type": "comment",
              "name": "<name>",
              "content": "<content>"
              "zone": "<zonename>,
              "zone_id": "<zoneid>"
            }
        """
        LOG.info("api search terms: %s", search_term)
        results = self._get('%s/search-data?q=%s&max=%d' % (
            self.url,
            search_term,
            max_result
        ))
        LOG.info("%d search result(s)", len(results))
        LOG.debug("search results: %s", results)
        return results

    # pylint: disable=inconsistent-return-statements
    def get_zone(self, name):
        """Get zone by name

        :param str name: Zone name (canonical)
        :return: Zone as :class:`PDNSZone` instance or :obj:`None`

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#zone95collection
        """
        LOG.info("getting zone: %s", name)
        for zone in self._zone_list:
            if zone.name == name:
                LOG.debug("found zone: %s", zone)
                return zone
        LOG.info("zone not found: %s", name)

    def suggest_zone(self, r_name):
        """Suggest best matching zone from existing zone

        Proposal is done on longer zone names matching the record suffix.
        Example::

            record: a.test.sub.domain.tld.
            zone:              domain.tld.
            zone:          sub.domain.tld.   <== best match
            zone:      another.domain.tld.

        :param str r_name: Record canonical name
        :return: Zone as :class:`PDNSZone` object
        """
        LOG.info("suggesting zone for: %s", r_name)
        if not r_name.endswith('.'):
            raise PDNSCanonicalError(r_name)
        best_match = ""
        for zone in self.zones:
            if r_name.endswith(zone.name):
                if not best_match:
                    best_match = zone
                if len(zone.name) > len(best_match.name):
                    best_match = zone
        LOG.info("zone best match: %s", best_match)
        return best_match

    def create_zone(self, zone):
        """
            Creates a new zone on current server
            :param zone: new zone object
            :return zone: created zone
        """
        zone.create(self)
        return zone

    def delete_zone(self, name):
        """Delete a zone

        :param str name: Zone name
        :return: :class:`PDNSApiClient` response
        """
        # reset server object cache
        self._zones = None
        LOG.info("deletion of zone: %s", name)
        return self._delete("%s/zones/%s" % (self.url, name))