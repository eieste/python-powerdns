import json
import os
import copy
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

    def __init__(self, server=None, id=None, name=None, type="Zone", url=None, kind=None, rrsets=None, rrset_list=[], serial=int,
                 notified_serial=int, masters=[], dnssec=False, nsec3param=None, nsec3narrow=False, presigned=False,
                 soa_edit=None, soa_edit_api=None, api_rectify=False, zone=None, account=None, nameservers=[],
                 tsig_mater_key_ids=[], tsig_slave_key_ids=[]):

        super(PDNSZone, self).__init__(server)

        if len(rrset_list) > 0 and rrsets is not None:
            raise LookupError("Please define only rrset_list OR rrsets")


        if rrsets is not None:
            rrsets = [RRSet.parse(self, rrset) for rrset in rrsets]

        if rrset_list is not None:
            rrsets = rrset_list

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

        #: Delete keys with default vaules from detail list
        details = copy.copy(self._details)

        for key, value in self._details.items():
            if value is self.DEFAULTS[key]:
                del details[key]

        self._details = details

        if server:
            self.refresh()


    @classmethod
    def parse(cls, server, raw_data):
        raw_data.pop("url")
        raw_data.pop("last_check")
        # ToDo parse rrsets
        return cls(server, **raw_data)

    def refresh(self):
        raw_data = self._load_details()
        raw_data["rrsets"] = [RRSet.parse(self, data) for data in raw_data["rrsets"]]
        raw_data.pop("url")
        self._details.update(raw_data)

    def set(self, name, value):
        self._details[name] = value

    def get(self, name):
        return self._details[name]

    def json(self):
        return self._details

    def create(self, server):
        """
            Creates a new zone
            :param server: Instance of server
            :return zone: Created Zone
        """
        self._parent = server

        self.patch_methods(self.get_api_client())

        zone_data = self._post("{}/zones".format(self._parent.get_url()), data=self.json())
        LOG.debug(zone_data)
        return self

    def save(self):
        if self._parent is None:
            raise AttributeError("Missing Server linkiing")
        zone_data = self._details

        #if len(self.get("rrsets")) > 0:
        #    zone_data["rrsets"] = self.rrset_list

        zone_info = self._patch("{}/zones/{}".format(self._parent.get_url(), self.get("id")), data=zone_data)

    def get_url(self):
        return "{}/zones/{}".format(self._parent.get_url(), self.get("name"))

    def _load_details(self):
        raw_data = self._get(self.get_url())
        return raw_data

    def get_rrset(self, name):
        """
        Get record data

        :param str name: Record name
        :return: Records rrset
        """
        for rr in self.get("rrsets"):
            if name == rr.get("name"):
                return rr

    def append_rrset(self, rrset):
        assert isinstance(rrset, RRSet)
        rrsets = self.get("rrsets")
        rrset._zone = self
        rrsets.append(rrset)
        self.set("rrsets", rrsets)
