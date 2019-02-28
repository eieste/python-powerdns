# -*- coding: utf-8 -*-
#
#  PowerDNS web api python client and interface (python-powerdns)
#
#  Copyright (C) 2018 Denis Pompilio (jawa) <dpompilio@vente-privee.com>
#
#  This file is part of python-powerdns
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the MIT License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  MIT License for more details.
#
#  You should have received a copy of the MIT License along with this
#  program; if not, see <https://opensource.org/licenses/MIT>.

"""
powerdns.interface - PowerDNS API interface
"""

import logging
LOG = logging.getLogger(__name__)


class PDNSEndpointBase(object):
    """Powerdns API Endpoint Base

        :param PDNSApiClient api_client: Cachet API client instance
    """
    def __init__(self, up):
        """Initialization method"""
        api_client = self.get_api_client(up)
        self._get = api_client.get
        self._post = api_client.post
        self._patch = api_client.patch
        self._put = api_client.put
        self._delete = api_client.delete


    def get_api_client(self, up):
        from powerdns.models.endpoint import PDNSEndpoint

        if isinstance(up, PDNSEndpoint):
            return up._api_client
        else:
            return up.get_api_client(up.get_parent())