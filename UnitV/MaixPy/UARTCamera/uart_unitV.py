import sensor
import array

class UART:
    def __init__(self, checkInterval):
        from machine import Timer
        self.timer = Timer(Timer.TIMER0, Timer.CHANNEL0, start=False, callback=self.inputCheck, period=checkInterval, mode=Timer.MODE_PERIODIC)
    checking = False
    uart = False
    timer = False
    def connect(self):
        from fpioa_manager import fm
        import machine
        fm.register(35, fm.fpioa.UART2_RX, force=True)
        fm.register(34, fm.fpioa.UART2_TX, force=True)
        self.uart = machine.UART(machine.UART.UART2, 115200, 8, 0, 2, timeout=1000, read_buf_len=4096)
        self.uart.init()
        self.timer.start()
        return self.uart

    def inputCheck(self, timerobj):
        if (self.uart.any() > 0 and self.checking == False):
            self.checking = True
            self.checking = self.onMessage(actionManager)

    def onMessage(self, callback):
        while self.uart.any() > 0:
            msg = self.uart.readline()
            print("new message")
            print(msg)
            if callback != None:
                callback(msg.decode("utf-8"), self)
        return False

def pic2PixelByteArray(img):
    print("encoding")
    w = 80 if img.width() > 80 else img.width()
    h = img.height()
    offset = 24
    arr = array.array('i', [w, h, 0])
    for i in range(0, h):
        for j in range(offset, w + offset):
            pixcolor = rgbToInt(img.get_pixel(j, i))
            arr.append(pixcolor)
    return bytearray(arr)

def rgbToInt(RGBlist):
    return (RGBlist[0] << 0x10) + (RGBlist[1] << 0x8) + RGBlist[2]

class Camera:
    isOn = False
    mode = sensor.RGB565
    frame = sensor.QQVGA2
    def shoot(shutdown = False):
        import sensor
        if not Camera.isOn:
            sensor.reset()
            sensor.set_vflip(True)
            sensor.set_hmirror(True)
            sensor.set_pixformat(Camera.mode)
            sensor.set_framesize(Camera.frame)
            sensor.skip_frames(10)
        pic = sensor.snapshot()
        sensor.shutdown(shutdown)
        Camera.isOn = not shutdown
        return pic

def actionManager(msg, uart):
    def takePhoto():
        print("taking photo")
        pic = Camera.shoot()
        uart.uart.write(b"picIncoming\n")
        barr = pic2PixelByteArray(pic)
        uart.uart.write(bytearray(repr(len(barr)) + "\n"))
        print("sending " + repr(len(barr)) + " bytes")
        uart.uart.write(barr)
        print("photo sent")
        del barr
    switch = {
            'takePhoto\n': takePhoto()
    }
    if msg in switch:
        return switch[msg]

uart = UART(50)
uart.connect()
