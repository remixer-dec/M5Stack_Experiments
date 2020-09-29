import machine
import time
import array
import gc

class UART:
    def __init__(self, checkInterval=250, callback=None):
        self.checking = False
        self.sending = False
        self.uart = machine.UART(1, tx=32, rx=33)
        self.timer = machine.Timer(8457)
        self.callback = callback
        self.checkInterval = checkInterval
        
    def connect(self):
        self.uart.init(115200, bits=8, parity=None, stop=1)
        self.timer.init(period=self.checkInterval, mode=machine.Timer.PERIODIC, callback=self.inputCheck)
        return self.uart
    
    def send(self, data):
        if self.sending:
            return
        ts = time.time()
        while self.checking:
            if time.time() - ts < 3:
                pass
            else:
                self.checking = False
        self.sending = True
        self.uart.write(data)
        self.sending = False

    def inputCheck(self, timerobj):
        if (self.uart.any() > 0 and self.checking is False):
            self.checking = True
            self.onMessage()
        
    def onMessage(self):
        while self.uart.any() > 0:
            msg = self.uart.readline()
            #print(msg)
            if self.callback:
                self.callback(msg)
            else:
                self.checking = False
        return

def actionManager(msg):
    actions = {b'picIncoming\n': getPhoto}
    if msg in actions:
        actions[msg]()
    else:
        uart.checking = False

def getPhoto():
    global uart, camPic
    uart.checking = True
    try:
        while uart.uart.any() < 2:
            pass
    
        size = uart.uart.readline()
        size = int(size.decode("utf-8"))
    
        receivedSize = 0
        receivedBytes = bytearray(size)
        ts = time.time()
        
        while receivedSize < size:
            while uart.uart.any() == 0 and time.time() - ts < 3:
                pass
            if not uart.uart.any():
                del receivedBytes
                uart.checking = False
                return
            ts = time.time()
            chunkSize = uart.uart.any()
            ba = bytearray(chunkSize)
            uart.uart.readinto(ba, chunkSize)
            receivedBytes[receivedSize:receivedSize+chunkSize] = ba
            receivedSize += chunkSize
            del ba

        camPic = receivedBytes
    except:
        gc.collect()
        print(b'NOT ENOUGH RAM')
        time.sleep_ms(40)
        while uart.uart.any():
            uart.uart.read(uart.uart.any())
            time.sleep_ms(40)
    uart.checking = False
    return


class RemoteAction:
    def configure(*args):
        global camCfg
        camCfg = tuple(args)
        uart.send(b'configure\n')
        uart.send(b''+"_".join(map(str, camCfg)) + '\n')
    
    def takePhoto():
        uart.send(b'takePhoto\n')
        
class Backend:
    def whitelist(src):
        def isAllowed(req, res):
            if req.GetIPAddr() in allowedIPs:
                src(req, res)
            else:
                return res.WriteResponseBadRequest()
        return isAllowed
    
    def parseParams(params, keys):
        output = array.array('h')
        for key in keys:
            if key in params:
                output.append(int(params[key]))
            else:
                output.append(0)
        return output
    
    @whitelist
    def setCfgPage(req, res):
        params = req.GetRequestQueryParams()
        res.WriteResponse(204, (), '', '', '')
        RemoteAction.configure(*Backend.parseParams(params,
            ('res', 'color', 'filter1', 'filter2', 'nn',
             'contrast', 'bright', 'sat', 'gain', 'flash')))
    @whitelist
    def getCfgPage(req, res):
        res.WriteResponse(200, (), 'text/javascript', 'utf-8', 'setConfig'+repr(camCfg)+'')
        
    @whitelist
    def camImage(req, res):
        global camPic
        try:
            RemoteAction.takePhoto()
            res.WriteResponse(200, {'Cache-Control': 'no-cache, max-age=0'},
                              'image/jpeg', 'binary', camPic)
        except:
            gc.collect()




from MicroWebSrv.microWebSrv import MicroWebSrv

import wifi
wifi.connect()
allowedIPs = ('192.168.1.45', '192.168.1.33')

camPic = b''
camCfg = (4, 0, 0, 0, 0, 10, 0, 0, 3, 0)

mws = MicroWebSrv(routeHandlers=[
    ('/img.jpg','GET', Backend.camImage),
    ('/setcfg', 'GET', Backend.setCfgPage),
    ('/getcfg', 'GET', Backend.getCfgPage)
    ], webPath="/flash/www")
mws.Start(threaded=True)

uart = UART(32, callback=actionManager)
uart.connect()
time.sleep(2)
uart.send(b'takePhoto\n')