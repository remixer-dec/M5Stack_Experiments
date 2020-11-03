import sensor
import image

try:
    from modules import ws2812
except ImportError:
    class ws2812():
        def __init__(self, p1, p2):
            pass
        def set_led(self, a, b):
            pass
        def display(self):
            pass

LED = ws2812(8,1)

RES = [sensor.VGA, sensor.QVGA, sensor.QQVGA, sensor.QQVGA2, sensor.CIF, sensor.SIF, sensor.B128X128, sensor.B64X64]
CLR = [sensor.RGB565, sensor.GRAYSCALE, sensor.YUV422]


class UART:
    def __init__(self, checkInterval,callback):
        from machine import Timer
        self.callback = callback
        self.timer = Timer(Timer.TIMER0, Timer.CHANNEL0, start=False, callback=self.inputCheck, period=checkInterval, mode=Timer.MODE_PERIODIC)
        self.checking = False
        self.sending = False
        self.uart = False

    def connect(self):
        from fpioa_manager import fm
        import machine
        fm.register(35, fm.fpioa.UARTHS_RX, force=True)
        fm.register(34, fm.fpioa.UARTHS_TX, force=True)
        self.uart = machine.UART(machine.UART.UARTHS, 115200, 8, 0, 1, timeout=1000, read_buf_len=4096)
        self.uart.init()
        self.timer.start()
        return self.uart

    def send(self, data):
        if not self.sending:
            self.sending = True
            self.uart.write(data)
            self.sending = False

    def inputCheck(self, timerobj):
        if (self.uart.any() > 0 and self.checking == False):
            self.checking = True
            self.checking = self.onMessage(self.callback)

    def onMessage(self, callback):
        while self.uart.any() > 0:
            msg = self.uart.readline()
            if callback != None:
                callback(msg)
        return False

class Camera:
    isOn = False
    mode = sensor.RGB565
    frame = sensor.CIF
    brightness = 0
    contrast = 1
    saturation = 0
    postproc = 0
    filter1 = 0
    filter2 = 0
    flash = 0

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
        pic.gamma_corr(1, Camera.contrast, Camera.brightness)
        if Camera.filter1 > 0:
            postProcess.applyFilter(Camera.filter1, pic)
        if Camera.filter2 > 0:
            postProcess.applyFilter(Camera.filter2, pic)
        if Camera.postproc == 1:
            postProcess.faceDetect(pic)

        sensor.shutdown(shutdown)
        Camera.isOn = not shutdown
        return pic

class Action:
    def takePhoto():
        try:
            pic = Camera.shoot()
            uart.send(b'picIncoming\n')
            picb = pic.compress().to_bytes()
            uart.send(str(len(picb)) + "\n")
            uart.send(picb)
            del pic
            del picb
        except MemoryError:
            print('NOT ENOUGH RAM, IT WAS ENOUGH IN PREVIOUS VERSIONS OF THIS FIRMWARE')

    def setConfig():
        while not uart.uart.any() > 0:
            pass
        uart.checking = True
        data = uart.uart.readline()
        data = data.decode('ascii')
        data = list(map(int, data.split('_')))
        Camera.frame = RES[data[0]]
        Camera.mode = CLR[data[1]]
        Camera.filter1 = data[2]
        Camera.filter2 = data[3]
        Camera.postproc = data[4]
        Camera.contrast = data[5] / 10
        Camera.brightness = data[6] / 10
        Camera.saturation = data[7]
        sensor.set_gainceiling(2**(data[8] if data[8] > 0 and data[8] < 8 else 3))
        Camera.flash = data[9] if data[9] <= 255 and data[9] >= 0 else 0
        LED.set_led(0, (Camera.flash, Camera.flash, Camera.flash))
        LED.display()
        sensor.set_pixformat(Camera.mode)
        sensor.set_framesize(Camera.frame)
        sensor.set_saturation(Camera.saturation)
        uart.checking = False

    def actionManager(msg):
        actions = {b'takePhoto\n': Action.takePhoto, b'configure\n': Action.setConfig}
        if msg in actions:
            return actions[msg]()

class postProcess:
    faceCascade = image.HaarCascade('frontalface')

    def applyFilter(fid, img):
        f = [None, lambda i: i.gaussian(1), lambda i: i.histeq(), lambda i: i.mean(1),
         lambda i: i.mean(1), lambda i: i.erode(2),
         lambda i: i.dilate(2), lambda i: i.chrominvar() if i.format() == 2 else i,
         lambda i: i.illuminvar() if i.format() == 2 else i]
        return f[fid](img)

    def detectFace(img):
        f = img.find_features(postProcess.faceCascade, 0.9)
        if f:
            img.draw_rectangle(*f)


uart = UART(32, callback=Action.actionManager)
uart.connect()
