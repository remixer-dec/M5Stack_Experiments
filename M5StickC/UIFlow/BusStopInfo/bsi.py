import urequests as rq
import gc

import wifi
wifi.connect()

API_URL = 'https://yandex.ru/maps/api/'
yUID = ''
csrftoken = ''
BUS_STOP = 'stop__9642916'
    
def getBusStopInfo(stop_id ):
    global csrftoken, yUID
    
    def GET(url, headers = {}):
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3945.88 Safari/537.36'
        return rq.get(url, headers=headers)
        
    def getCSRFToken():
        return GET(API_URL, {'Cookie': 'yandexuid=' + yUID}).json()["csrfToken"]

    @micropython.native
    def sign(s) -> int:
        from array import array
        t = len(s)
        n = array('i', [5381])
        for r in range(t):
            n[0] = 33 * n[0] ^ ord(s[r])
        return 4294967296 + n[0] if n[0] < 0 else n[0]
    
    def formQueryString(d):
        query = ""
        for key in d.keys():
            query += str(key) + "=" + str(d[key]) + "&"
        return query[:-1]

    def formReqObj(token, stopid, sid):
        from collections import OrderedDict
        return OrderedDict([('ajax', 1), ('csrfToken', token.replace(':', '%3A')), ('id', stopid), ('lang', 'ru'),
                            ('locale', 'ru_RU'), ('mode', 'prognosis'),('sessionId', sid)])
        
    def formRequest(query):
        url = API_URL + 'masstransit/getStopInfo?' + query
        ref = 'https://yandex.ru/maps/213/moscow/?l=masstransit&mode=masstransit'
        return GET(url, headers = {'x-retpath-y': ref, 'referrer': ref, 'cookie': 'yandexuid={}'.format(yUID)})
    
    def getClearedData(resp):
        global csrftoken
        
        resp = resp.json()
        if not 'data' in resp:
            if 'csrftoken' in resp:
                csrftoken = resp['csrftoken']
            return False
        
        del resp['data']['region']
        del resp['data']['breadcrumbs']
        gc.collect()
        for n in resp['data']['transports']:
            del n['lineId']
            n['name'] = n['seoname']
            del n['seoname']
            del n['Types']
            del n['uri']
            n['times'] = n['threads'][0]['BriefSchedule']['Events']
            del n['threads']
        gc.collect()
        return resp
    
    def getYUIDCookie(url):
        import socket
        _, _, host, path = url.split('/', 3)
        addr = socket.getaddrinfo(host, 443)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        response = ''
        while True:
            data = s.recv(100)
            if data:
                response += str(data, 'utf8')
            else:
                break
        s.close()
        rcontent = response.split('\r\n', 1)[1].split('\r\n\r\n')
        for h in rcontent[0].split('\r\n'):
            hk, hv = h.split(': ', 1)
            if hk == 'Set-Cookie':
                if hv[:9] == 'yandexuid':
                    return hv[10:hv.find(';')]
        
    if not yUID:
        yUID = getYUIDCookie(API_URL)
    if not csrftoken:
        csrftoken = getCSRFToken()
    reqObj = formReqObj(csrftoken, stop_id, csrftoken.split(':')[1]+'000_543210')
    qstr = formQueryString(reqObj)
    reqObj['s'] = str(sign(qstr))
    qstr = formQueryString(reqObj)
    return getClearedData(formRequest(qstr))
    
def BSIApp():
    from m5stack import lcd, btnA, btnB, rtc
    from machine import Timer
    import _thread
    
    lcd.font(lcd.FONT_Small)
    info = False
    xCenter = (0, 9, 5, 0, -4, -4)
    order = False
    mode = 1
    
    def updateBusDataThreaded(tmr=False):
        _thread.start_new_thread(updateBusData, tuple())

    def updateBusData():
        nonlocal info
        info = False
        print('updating')
        info = getBusStopInfo(BUS_STOP)
        drawBusData()
        gc.collect()
        
    def drawBusData():
        if not info:
            return
        
        lcd.clear(0xffffff)
        offsetY = 2
        offsetX = 35        
        info['data']['transports'].sort(reverse=order, key= \
            lambda x: int(getBusTimeData(x['times'][0])['value']) if len(x['times']) > 0 else float('inf'))
        
        for i, t in enumerate(info['data']['transports']):
            lcd.fillRoundRect(2, offsetY, 30, 12, 2, getVehicleColor(t['type']))
            lcd.text(6 + xCenter[len(t['name'])], offsetY, t['name'], 0xffffff)
            if len(t['times']) > 0:
                if mode == 0:
                    target = getBusTimeData(t['times'][0])
                    lcd.text(32, offsetY, target['text'], 0)
                else:
                    currentTime = info['data']['currentTime'] // 1000 + info['data']['tzOffset']
                    for k,v in enumerate(t['times']):
                        target = getBusTimeData(v)
                        arrivalTime = int(target['value']) + int(target['tzOffset'])
                        waitTime = str(getMinuteWaitTime(currentTime, arrivalTime))
                        lcd.fillRoundRect(1 + offsetX, offsetY, 20, 12, 2, getWaitTimeColor(int(waitTime)))
                        if len(waitTime) > 2:
                            waitTime = str(int(waitTime) // 60 + 1) + 'H'
                        lcd.text(offsetX + xCenter[len(waitTime)], offsetY, waitTime, 0xffffff)
                        offsetX += 22
                        if k == 1:
                            break
                    offsetX = 35
            offsetY += 13
            if i == 10:
                break
        displayTime()
    
    def getBusTimeData(src):
        return src['Estimated' if 'Estimated' in src else 'Scheduled']
        
    def getMinuteWaitTime(currentTime, busTime):
        return round((busTime - currentTime) / 60)
    
    def getWaitTimeColor(wt: int) -> int:
        return 0x3cb300 * int(wt <= 10) + 0xfce513 * int(wt > 10 and wt <= 16) + 0xfe7613 * (wt > 16 and wt <= 25) + 0xff2812 * int(wt > 25)
            
    def getVehicleColor(vtype):
        return int(vtype == 'bus' or vtype == 'trolleybus') * 0x3377e4 + int(vtype == 'minibus') * 0xb43dcc \
            + int(vtype == 'tramway') * 0xf43000 + int(vtype == 'suburban') * 0x777000

    def displayTimeThreaded(tmr = False):
        _thread.start_new_thread(displayTime, tuple())

    @micropython.native
    def displayTime():
        time = rtc.now()
        txt = '{:02d}:{:02d}:{:02d}'.format(*time[-3:])
        lcd.textClear(9, 148, txt, 0xFFFFFF)
        lcd.text(9, 148, txt, 0)

    syncTime()        
    updateBusData()
    timeTimer = Timer(8005)
    updateTimer = Timer(8006)
    timeTimer.init(period=1000, mode=Timer.PERIODIC, callback=displayTimeThreaded)
    updateTimer.init(period=30000, mode=Timer.PERIODIC, callback=updateBusDataThreaded)
    
    while True:
        if btnA.isPressed():
            order = not order
            drawBusData()
            while btnA.isPressed():
                pass
        if btnB.isPressed():
            mode = not mode
            drawBusData()
            while btnB.isPressed():
                pass
            
def syncTime():
    from m5stack import rtc
    from ntptime import client
    n = client(host='pool.ntp.org', timezone=3)
    n.updateTime()
    rtc.setTime(*n.time[:-1])
    del n
    
if __name__ == '__main__':
    BSIApp()