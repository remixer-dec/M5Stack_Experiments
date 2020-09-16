from m5stack import lcd, btnA, btnB
from PNGdecoder import png
import wifi
import gc
from array import array

wifi.connect()
del wifi


def getMap(lon, lat, zoom, pitch):
    import urequests as rq
    MAPBOX_TOKEN = ''
    HEIGHT = 148
    return rq.get(
        'https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/{},{},{},{},{}/80x{}?access_token={}'
        .format(lon, lat, zoom, 0, pitch, HEIGHT, MAPBOX_TOKEN)).content


def drawControls():
    lcd.fillRect(0, 148, 80, 11, 0x2b4860)
    pos = array('b', (4, 14, 24, 34, 44, 48, 54, 58, 66, 68, 70))
    txt = '+-<>/\\\\/...'
    for i, char in enumerate(txt):
        lcd.text(pos[i], 148, char, 0xffffff)


class SelectionManagerV2:
    def __init__(self, smtype=0, total=2, callback=print):
        self.total = total
        self.sel = 0
        self.type = smtype
        self.callback = callback

    def loop(self):
        self.callback(self)
        while True:
            if btnA.isPressed():
                while btnA.isPressed():
                    pass
                return self.sel
            if btnB.isPressed():
                self.sel = self.sel + 1 if self.sel < self.total - 1 else 0
                while btnB.isPressed():
                    pass
                self.callback(self)


def selectionRenderer(smInstance):
    oldSel = smInstance.sel - 1 if smInstance.sel - 1 >= 0 else smInstance.total - 1
    if smInstance.type == 0:
        lcd.fillRect(2, 22 + 12 * smInstance.sel, 76, 12, 0x88bfb9)
        lcd.fillRect(2, 22 + 12 * oldSel, 76, 12, 0x2b4860)
        mainMenuText()
    else:
        lcd.drawRect(smInstance.sel * 10, 148,
                     4 + (10 if smInstance.sel < 4 else 12), 12, 0x88bfb9)
        lcd.drawRect(oldSel * 10, 148, 4 + (10 if oldSel < 4 else 12), 12,
                     0x2b4860)


def mainMenuText():
    lcd.text(lcd.CENTER, 22, 'World Map')
    lcd.text(lcd.CENTER, 34, 'Search')
    lcd.text(lcd.CENTER, 46, 'Find me')
    lcd.text(lcd.CENTER, 58, 'Exit')


def mainMenu():
    def worldMap():
        return mapView

    def leave():
        import sys
        sys.exit()

    lcd.clear(0x2b4860)
    lcd.fillRect(0, 0, 80, 12, 0xc6585a)
    lcd.font(lcd.FONT_Arial12)
    lcd.text(lcd.CENTER, 0, 'MAPS', 0xFFFFFF)
    lcd.font(lcd.FONT_Small)
    callbacks = (worldMap, search, findMe)
    s = SelectionManagerV2(0, 4, selectionRenderer).loop()
    return callbacks[s]


LRzoomFactors = array('f', (30, 0, 10, 0, .5, 0, .4, 0, .1, 0, .04, 0, .01, 0, .002, 0, .0005, 0, .0002, 0, .00005))
UDzoomFactors = array('f', (0, 0, 5, 0, 1, 0, .5, 0, .2, 0, .05, 0, .01, 0, .005, 0, .0005, 0, .0001, 0, .00005))


class MapData:
    def __init__(self, lon, lat, zoom, pitch):
        self.lon = lon
        self.lat = lat
        self.pitch = pitch
        self.zoom = zoom

    def scaleUp(self):
        self.zoom = self.zoom + 2 if self.zoom < 20 else 20
        return self

    def scaleDown(self):
        self.zoom = self.zoom - 2 if self.zoom > 0 else 0
        return self

    def moveLeft(self):
        self.lon -= LRzoomFactors[self.zoom]
        return self.fixLimits()

    def moveRight(self):
        self.lon += LRzoomFactors[self.zoom]
        return self.fixLimits()

    def moveUp(self):
        self.lat += UDzoomFactors[self.zoom]
        return self.fixLimits()

    def moveDown(self):
        self.lat -= UDzoomFactors[self.zoom]
        return self.fixLimits()

    def fixLimits(self):
        if self.lon < -180:
            self.lon = 180 + (180 - self.lon)
        if self.lon > 180:
            self.lon = -180 + (self.lon - 180)
        if self.lat < -85.0511:
            self.lat = 85.0511 + (85.0511 - self.lon)
        if self.lat > 85.0511:
            self.lat = -85.0515 + (self.lat - 85.0511)
        return self

#Longitude must be between -180-180
#Latitude must be between -85.0511-85.0511.

def mapView(lon=0, lat=0, zoom=0):
    m = MapData(lon, lat, zoom, 50)
    try:
        img = png(getMap(lon, lat, zoom, 50),
                  callback=lcd.drawPixel).render(0, 0)
        del img
    except MemoryError:
        lcd.text(0, 10, 'Not enough RAM', 0)
    gc.collect()
    sm = SelectionManagerV2(1, 7, selectionRenderer)
    while True:
        drawControls()
        s = sm.loop()
        callbacks = (m.scaleUp, m.scaleDown, m.moveLeft, m.moveRight, m.moveUp,
                     m.moveDown, mainMenu)
        if s != 6:
            callbacks[s]()
            del callbacks
            try:
                img = png(getMap(m.lon, m.lat, m.zoom, m.pitch),
                          callback=lcd.drawPixel).render(0, 0)
                del img
            except MemoryError:
                lcd.text(0, 10, 'Not enough RAM', 0)
            gc.collect()
        else:
            return mainMenu


def findMe():
    from geolocate import findDevice
    coords = findDevice()
    del findDevice
    gc.collect()
    return mapView(coords[0], coords[1], 12)


def search():
    from accelKeyboard import Keyboard
    from geolocate import findPlace
    inputText = Keyboard().loop()
    coords = findPlace(inputText)
    del Keyboard
    del inputText
    del findPlace
    if coords:
        gc.collect()
        return mapView(coords[0], coords[1], 14 if coords[2] != 'city' else 8)
    else:
        lcd.clear()
        lcd.text(0, 20, 'Place not Found')
        lcd.text(lcd.CENTER, 100, 'ok')
        while not btnA.isPressed() or btnB.isPressed():
            while btnA.isPressed() or btnB.isPressed():
                pass
        return search


def mainLoop():
    item = mainMenu
    while True:
        item = item()

mainLoop()