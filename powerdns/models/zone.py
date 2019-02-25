import json
import os

from powerdns.interface import PDNSEndpointBase, LOG
from powerdns.models.rrset import RRSet


class PDNSZone(PDNSEndpointBase):
    """Powerdns API Zone Endpoint

    .. autoattribute:: details
    .. autoattribute:: records

    :param PDNSApiClient api_client: Cachet API client instance
    :param PDNSServer server: PowerDNS server instance
    :param dict api_data: PowerDNS API zone data
    """

    DEFAULTS = {
        "id": None,
        "name": None,
        "type": "Zone",
        "url": None,
        "kind": None,
        "rrsets": None,
        "rrset_list": [],
        "serial": int,
        "notified_serial": int,
        "masters": [],
        "dnssec": False,
        "nsec3param": None,
        "nsec3narrow": False,
        "presigned": False,
        "soa_edit": None,
        "soa_edit_api": None,
        "api_rectify": False,
        "zone": None,
        "account": None,
        "nameservers": [],
        "tsig_mater_key_ids": [],
        "tsig_slave_key_ids": [],
    }

    def __init__(self, server, id=None, name=None, type="Zone", url=None, kind=None, rrsets=None, rrset_list=[], serial=int,
                 notified_serial=int, masters=[], dnssec=False, nsec3param=None, nsec3narrow=False, presigned=False,
                 soa_edit=None, soa_edit_api=None, api_rectify=False, zone=None, account=None, nameservers=[],
                 tsig_mater_key_ids=[], tsig_slave_key_ids=[]):

        self._server = server
        super(PDNSZone, self).__init__(server)

        if len(rrset_list) > 0 and rrsets is not None:
            raise LookupError("Please define only rrset_list OR rrsets")

        self.rrset_list = rrset_list
        print(rrsets)
        print("*"*50)
        if rrsets is not None:
            self.rrset_list = [RRSet.parse(data) for data in rrsets]

        self._details = {
            "id": id,
            "name": name,
            "type": type,
            "url": url,
            "kind": kind,
            "serial": serial,
            "notified_serial": notified_serial,
            "masters": masters,
            "rrsets": rrsets,
            "dnssec": dnssec,
            "nsec3param": nsec3param,
            "nsec3narrow": nsec3narrow,
            "presigned": presigned,
            "soa_edit": soa_edit,
            "soa_edit_api": soa_edit_api,
            "api_rectify": api_rectify,
            "zone": zone,
            "account": account,
            "nameservers": nameservers,
            "tsig_mater_key_ids": tsig_mater_key_ids,
            "tsig_slave_key_ids": tsig_slave_key_ids
        }

        raw_data = self._load_details()
        self.rrset_list = [RRSet.parse(self, data) for data in raw_data["rrsets"]]
        self._details.update(raw_data)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'PDNSZone:%s:%s' % (self._server.id, self.name)

    def set(self, name, value):
        self._details[name] = value

    def get(self, name):
        return self._details[name]

    def get_parent(self):
        return self._server

    @classmethod
    def parse(cls, server, raw_data):
        raw_data.pop("url")
        raw_data.pop("last_check")
        # ToDo parse rrsets
        return cls(server, **raw_data)

    def create(self):
        zone_data = self._details
        zone_data = self._post("{}/zones".format(self._server.get_url()), data=zone_data)
        print(zone_data)

    def save(self):
        zone_data = self._details

        if len(self.rrset_list) > 0:
            zone_data["rrsets"] = self.rrset_list

        zone_info = self._patch("{}/zones/{}".format(self._server.get_url(), self.get("id")), data=zone_data)
        print(zone_info)

    def get_url(self):
        return "{}/zones/{}".format(self._server.get_url(), self.get("name"))

    def _load_details(self):
        raw_data = self._get(self.get_url())
        return raw_data

    def get_rrset_list(self):
        return self.rrset_list

    # pylint: disable=inconsistent-return-statements
    def get_record(self, name):
        """Get record data

        :param str name: Record name
        :return: Records data as :func:`list`
        """
        records = []
        LOG.info("getting zone record: %s", name)
        for record in self.details['rrsets']:
            if name == record['name']:
                LOG.info("record found: %s", name)
                records.append(record)

        if not records:
            LOG.info("record not found: %s", name)

        return records

    def create_records(self, rrsets):
        """Create resource record sets

        :param list rrsets: Resource record sets
        :return: Query response
        """
        LOG.info("creating %d record(s) to %s", len(rrsets), self.name)
        LOG.debug("records: %s", rrsets)
        for rrset in rrsets:
            rrset.ensure_canonical(self.name)
            rrset['changetype'] = 'REPLACE'

        # reset zone object cache
        self._details = None
        return self._patch(self.url, data={'rrsets': rrsets})

    def delete_records(self, rrsets):
        """Delete resource record sets

        :param list rrsets: Resource record sets
        :return: Query response
        """
        LOG.info("deletion of %d records from %s", len(rrsets), self.name)
        LOG.debug("records: %s", rrsets)
        for rrset in rrsets:
            rrset.ensure_canonical(self.name)
            rrset['changetype'] = 'DELETE'

        # reset zone object cache
        self._details = None
        return self._patch(self.url, data={'rrsets': rrsets})

    def backup(self, directory, filename=None, pretty_json=False):
        """Backup zone data to json file

        :param str directory: Directory to store json file
        :param str filename: Json file name

        If filename is not provided, destination file is generated with zone
        name (stripping the last dot) and extension `.json`.
        """
        LOG.info("backup of zone: %s", self.name)
        if not filename:
            filename = self.name.rstrip('.') + ".json"
        json_file = os.path.join(directory, filename)
        LOG.info("backup file is %s", json_file)

        with open(json_file, "w") as backup_fp:
            if pretty_json:
                json.dump(self.details,
                          backup_fp,
                          ensure_ascii=True,
                          indent=2,
                          sort_keys=True)
            else:
                json.dump(self.details, backup_fp)
        LOG.info("zone %s successfully saved", self.name)