from m5stack import lcd, btnA, btnB
import gc

from wifi import connect
from JPEGdecoder import jpeg
from ticker import Ticker
from selectionManager import SelectionManager


tcfg = {'clientID': 'REPLACE_THIS_WITH_YOUR_CLIENT_ID', 'tickers': True, 'textBG': False}

gameFilter = ''
msgQueue = []
ticker = 0

def drawHeader():
    lcd.fillRect(0, 0, 80, 16, 0x6441a5)
    lcd.text(lcd.CENTER, 2, 'TwitchIoT')

def mainLoop():
    nextItem = mainMenu()
    while True:
        if isinstance(nextItem, list):
            nextItem = nextItem[0](nextItem[1])
        else:
            nextItem = nextItem()
        gc.collect()
        

def mainMenu(idk=0):
    global gameFilter
    gameFilter = ''
    lcd.font(lcd.FONT_Small)
    lcd.clear()
    drawHeader()
    lcd.text(lcd.CENTER, 20, 'Streams')
    lcd.text(lcd.CENTER, 40, 'Games')
    lcd.text(lcd.CENTER, 60, 'Users')
    lcd.text(lcd.CENTER, 80, 'Exit')
    def mainCallback(sel):
        return (streamsMenu, gamesMenu, searchMenu, leave)[sel]
    return SelectionManager(4, offsetY=18, callback=mainCallback).loop()

def leave():
    import sys
    sys.exit()
    
def loadAndDrawOnePreview(img, x, y):
    import urequests as rq
    try:
        img = img.replace('./', '')
        jpg = jpeg(rq.get(img).content, callback=lcd.drawPixel, quality=5).render(x, y)
        del jpg
    except (MemoryError, NotImplementedError):
        lcd.fillRect(x, y, 80, 44, 0x444444)
    gc.collect()

def trippleText(x, y, txt, clr):
    if tcfg['textBG'] is not False:
        lcd.textClear(x, y, txt, int(tcfg['textBG']))
    else:
        lcd.text(x, y+1, txt, 0)
        lcd.text(x, y-1, txt, 0)
    lcd.text(x, y, txt, clr)

def streamsMenu(streamOffset=0):
    ofy = 0
    data = twitchAPI('streams', {'limit': 3, 'offset': streamOffset, 'game': gameFilter})
    channels = []
    lcd.clear()
    lcd.drawLine(0, 0, 80, 0, 0x6441a5)
    for item in data['streams']:
       lcd.fillRect(0, ofy, 80, 45, 0x333333)
       lcd.text(lcd.CENTER, ofy+16,'LOADING')
       loadAndDrawOnePreview(item['preview']['small'], 0, 1+ofy)
       trippleText(2, ofy+2, item['channel']['name'], 0xffffff)
       channels.append(item['channel']['name'])
       trippleText(lcd.RIGHT, ofy+32, str(item['viewers']), 0xFF0000)
       ofy += 46
    del data
    lcd.text(4, 144, 'more', 0xFFFFFF)
    lcd.text(44, 144, 'back', 0xFFFFFF)
    def sc(n=0):
        return  selectChannel(channels[n])
        
    def channelCallback(sel):
        return [(sc, sc, sc, streamsMenu, mainMenu)[sel], (streamOffset+sel if sel == 3 else sel)]
        
    return SelectionManager(3, offsetY=1, boxH=46, callback=channelCallback, menu=2).loop()

def selectChannel(name):
    global ticker
    import uwebsockets.client as uwc
    lcd.clear()
    lcd.text(lcd.CENTER, 40, 'joining')
    lcd.text(lcd.CENTER, 60, 'chat')
    lcd.font(lcd.FONT_UNICODE)
    if tcfg['tickers']:
        ticker = Ticker(['']*9, 0xffffff, rotation=0, sliding=False, speed=16, delay=10, x=2, multiline=True)
    
    exitChat = False
    with uwc.connect('wss://irc-ws.chat.twitch.tv') as ws:
        ws.send('NICK justinfan123')
        #ws.send('CAP REQ :twitch.tv/tags')
        ws.send('JOIN  #' + name)
        msg = ws.recv()
        i = 0
        while msg.find('/NAMES') == -1:
            msg = ws.recv()
        msg = ws.recv()
        while not exitChat:
            if msg != '':
                #gc.collect()
                parseChatMsg(msg)
            msg = ws.recv()
            while btnB.isPressed():
                exitChat = True
        if tcfg['tickers']:
            ticker.stop()
            del ticker 
    return mainMenu

def parseChatMsg(msg):
    s = msg.split(':')
    username = s[1].split('!')[0]
    msg = s[2]
    del s
    renderChatMsg(username, msg)
    

def renderChatMsg(usr, msg):
    global msgQueue
    if len(msgQueue) > 8:
        msgQueue.pop(0)
    lcd.clear()
    msgQueue.append(usr+':' + msg)
    if tcfg['tickers']:
        for i in range(len(msgQueue)):
            ticker.text[i] = msgQueue[i]
    else:
        lcd.clear()
        lcd.text(0, 2, '\n'.join(msgQueue[-4:]))
        
def gamesMenu(itemOffset=0):
    ofy = 0
    data = twitchAPI('games/top', {'limit': 3, 'offset': itemOffset})
    games = []
    lcd.clear()
    lcd.drawLine(0, 0, 80, 0, 0x6441a5)
    for item in data['top']:
       lcd.fillRect(0, ofy, 80, 45, 0x333333)
       lcd.text(lcd.CENTER, ofy+16,'LOADING')
       loadAndDrawOnePreview(item['game']['box']['template']
                             .replace('{width}', '80').replace('{height}', '45'), 0 , 1+ofy)
       trippleText(2, ofy+2, item['game']['name'], 0xffffff)
       games.append(item['game']['name'])
       trippleText(lcd.RIGHT, ofy+32, str(item['viewers']), 0xFF0000)
       ofy += 46
    lcd.text(4, 144, 'more', 0xFFFFFF)
    lcd.text(44, 144, 'back', 0xFFFFFF)

    def gameCallback(sel):
        global gameFilter
        if sel < 3:
            if sel >= len(games):
                return mainMenu
            gameFilter = games[sel].replace(' ','+')
        return [(streamsMenu, streamsMenu, streamsMenu, gamesMenu, mainMenu)[sel], (itemOffset+sel if sel == 3 else 0)]
    return SelectionManager(3, offsetY=1, boxH=46, callback=gameCallback, menu=2).loop()

def searchMenu():
    from accelKeyboard import Keyboard
    channelName = Keyboard().loop()
    return selectChannel(channelName.lower())

def twitchAPI(method, params):
    import urequests as rq
    def _q(d):
        query = ""
        for key in d.keys():
            query += str(key) + "=" + str(d[key]) + "&"
        return query
    url = "https://api.twitch.tv/kraken/" + method +  "/?" + _q(params)
    return rq.get(url, headers={'accept':'application/vnd.twitchtv.v5+json', 'client-id': tcfg['clientID']}).json()

    
connect()
mainLoop()

