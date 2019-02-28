from powerdns.exceptions import PDNSCanonicalError
from powerdns.interface import LOG

class RRSet:
    """Resource record data for PowerDNS API

    :param str changetype: API keyword DELETE or REPLACE
    :param str name: Record name
    :param str rtype: Record type
    :param list records: List of Str or Tuple(content_str, disabled_bool)
    :param int ttl: Record time to live

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#url-apiv1serversserver95idzoneszone95id
    """
    def __init__(self, zone, name=None, rtype=None, records=None, ttl=3600, changetype='REPLACE'):

        self._zone = zone

        self._details = {
            "name": name,
            "rtype": rtype,
            "records": records,
            "ttl": ttl,
            "changetype": changetype
        }

        self._deleted_records = []

    def json(self):
        json = self._details
        json["type"] = json.pop("rtype")
        json["records"] += self._deleted_records
        return self._details


    def get(self, name):
        return self._details[name]

    def set(self, name, value):
        if name == "name" and self.get("name") is not None:
            raise ValueError("You cant change the Name. If you change the name anyway, please Create a new RRSet with the new Informations and delete this one")
        self._details[name] = value

    def __str__(self):
        pass
        # records = []
        #
        # for rr in self.raw_records:
        #     if isinstance(rr, tuple) or isinstance(rr, list):
        #         records += [rr[0]]
        #     else:
        #         records += [rr]
        #
        # return "(ttl=%d) %s  %s  %s)" % (self['ttl'],
        #                                  self['name'],
        #                                  self['type'],
        #                                  records)

    @classmethod
    def parse(cls, zone, raw_data):
        return cls(
            zone,
            name=raw_data["name"],
            rtype=raw_data["type"],
            records=raw_data["records"],
            ttl=raw_data["ttl"],
            changetype="REPLACE"
        )

    def ensure_canonical(self, zone):
        """Ensure every record names are canonical

        :param str zone: Zone name to build canonical names

        In case of CNAME records, records content is also checked.

        .. warning::

            This method update :class:`RRSet` data to ensure the use of
            canonical names. It is actually not possible to revert values.
        """
        LOG.debug("ensuring rrset %s is canonical", self['name'])
        if not zone.endswith('.'):
            raise PDNSCanonicalError(zone)
        if not self['name'].endswith('.'):
            LOG.debug("transforming %s with %s", self['name'], zone)
            self['name'] += ".%s" % zone
        if self['type'] == 'CNAME':
            for record in self['records']:
                if not record['content'].endswith('.'):
                    LOG.debug("transforming %s with %s",
                              record['content'], zone)
                    record['content'] += ".%s" % zone

    def mark_as_deleted(self):
        from powerdns.models.zone import PDNSZone
        if isinstance(self._zone, PDNSZone):
            self.set("changetype", "DELETE")
            self._zone.save()
        else:
            raise LookupError("This rrset is not 'connected' to a Zone")