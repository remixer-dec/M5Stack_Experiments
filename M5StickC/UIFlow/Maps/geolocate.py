def findDevice():
    import urequests as rq
    def getWifiNetworks():
        import network
        import ubinascii
        import ujson
        wlan = network.WLAN(network.STA_IF)
        scanned = wlan.scan()
        output = []
        for n in scanned:
            mac = ubinascii.hexlify(n[1]).decode('ascii')
            mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            output.append({"macAddress": mac, "signalStrength": n[3], "channel": n[2]})
        del scanned
        return ujson.dumps({'wifiAccessPoints': output})
    wifis = getWifiNetworks()
    coordsjson = rq.post('https://location.services.mozilla.com/v1/geolocate?key=geoclue',
                    headers={'Content-Type': 'application/json'}, data = wifis).json()
    coords = (coordsjson["location"]["lng"], coordsjson["location"]["lat"])
    return coords

def findPlace(txt):
    import urequests as rq
    results = rq.get(
        'https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1'
        .format(txt.replace('_', '+')),
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3945.88 Safari/537.36'
        })
    results = results.json()
    if len(results) > 0:
        r = (float(results[0]["lon"]), float(results[0]["lat"]),
             results[0]["type"])
        del results
        return r
    else:
        return False
