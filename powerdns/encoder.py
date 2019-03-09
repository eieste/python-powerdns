import json
from powerdns.models.rrset import RRSet
from datetime import timedelta


class PDNSJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        print(obj)
        if isinstance(obj, RRSet):
            return obj.json()
        elif isinstance(obj, timedelta):
            return int(obj.total_seconds())
        else:
            return obj

