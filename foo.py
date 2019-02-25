import powerdns

pdnsclient = powerdns.PDNSApiClient(**{
    "api_key": "changeme",
    "api_endpoint": "http://localhost:7080/api/v1"
})

pdnsextern = powerdns.PDNSEndpoint(pdnsclient)

zone_list = pdnsextern.get_server("localhost").get_zone_list()


iagle_net_zone = zone_list[0]

#iagle_net_zone.set("type", "Zone")
iagle_net_zone.save()