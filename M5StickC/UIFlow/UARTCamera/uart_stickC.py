import machine
import array
import gc
from m5stack import btnA, lcd

class UART:
    checking = False
    uart = machine.UART(1, tx=32, rx=33)
    timer = machine.Timer(8457)
    callback = None
    def connect(self, checkInterval=250):
        self.uart.init(115200, bits=8, parity=None, stop=2)
        self.timer.init(period=checkInterval, mode=machine.Timer.PERIODIC, callback=self.inputCheck)
        return self.uart

    def inputCheck(self, timerobj):
        if (self.uart.any() > 0 and self.checking == False):
            self.checking = True
            self.checking = self.onMessage()
        
    def onMessage(self):
        while self.uart.any() > 0:
            msg = self.uart.readline()
            print(msg)
            if self.callback:
                self.callback(msg,self)
        return False

@micropython.native
def actionManager(msg, uart):
    if(msg == b"picIncoming\n"):
        statusText("encoding\nphoto")
        uart.checking = True
        while uart.uart.any() == 0:
            pass
        size = uart.uart.readline()
        size = int(size.decode("utf-8"))
        while uart.uart.any() == 0:
            pass
        print("file transmission started")
        statusText("transferring\nphoto")
        received = 0
        imgarr = array.array('i')
        bytesLeft = bytearray([])
        while received < size:
            while uart.uart.any() == 0:
                pass
            bytesreceived = uart.uart.read(256)
            if bytesreceived:
                bytesLeft += bytesreceived
                received += len(bytesreceived)
                limiter = (len(bytesLeft) // 4) * 4
                imgarr.extend(bytesLeft[:limiter])
                bytesLeft = bytesLeft[limiter:]
                if received >= size:
                    imgarr.extend(bytesLeft)
                del bytesreceived
            #print('received ' + repr(received) + '/' + repr(size))
            gc.collect()
        print("file transmission ended, received:" + repr(len(imgarr)))
        uart.checking = False
        render(imgarr)
        del imgarr
        gc.collect()
        
@micropython.viper        
def render(arr):
    w = int(arr[0])
    h = int(arr[1])
    lcd.clear()
    for y in range(0, h):
        for x in range(0, w):
            lcd.drawPixel(x, y, arr[3 + x + y * w])

@micropython.viper
def statusText(text):
    lcd.fillRect(0, 0, 80, 32, 0)
    lcd.print(text, 0, 0)
    
def pressLoop():
    while True:
        if btnA.isPressed():
            lcd.clear()
            statusText("taking\nphoto")
            uart.uart.write(b'takePhoto')
            while not btnA.isReleased():
                pass
           
uart = UART()
uart.connect(50)
uart.callback = actionManager
lcd.font(lcd.FONT_DefaultSmall)
lcd.clear()
statusText("camera\nis ready")
pressLoop()