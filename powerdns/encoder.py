import json
from powerdns.models.rrset import RRSet



class PDNSJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, RRSet):
            return obj.json()
        else:
            return obj