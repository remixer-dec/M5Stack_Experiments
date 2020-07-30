from m5stack import lcd
from machine import Timer

class Ticker:
    _count = 0
    def __init__(self, text, color, rotation=3, sliding = True, limit=None, speed=250, x=0, y=0, delay=0):
        self._iterator = 0
        self._itdir = 1
        self._delayState = 0
        self.delay = delay
        self.sliding = sliding
        self.text = text
        self.color = color
        self.y = y
        self.x = x
        self.rotation = rotation
        self.limit = limit if limit else (7 if rotation % 2 == 0 else 14)
        self.timer = Timer(716839 + Ticker._count)
        self.timer.init(period=speed, mode=Timer.PERIODIC, callback=self._showText)
        Ticker._count += 1
    
    @micropython.native    
    def _showText(self, timercallbackvar=None):
        text = self.text
        if len(text) > self.limit:
            chunk = text[self._iterator:self._iterator + self.limit]
            if self._delayState < self.delay:
                self._delayState += 1
            else:
                self._iterator += self._itdir
            if self.sliding:
                if self._itdir == 1 and self._iterator >= (len(text) - self.limit):
                    self._itdir *= -1
                    self._delayState = 0
                if self._itdir == -1 and self._iterator == 0:
                    self._itdir *= -1
                    self._delayState = 0
            else:
                txtlen = len(text)
                if self._iterator >= txtlen - self.limit and self._iterator <= txtlen:
                    lcd.fillRect(self.x + len(chunk) * 4, self.y, 180, self.y + 15, 0)
                if self._iterator > txtlen and self._iterator < self.limit + txtlen:
                    offset = self.limit + txtlen - self._iterator 
                    chunk = ' ' * offset + text[:self._iterator - txtlen]
                if self._iterator >= self.limit + txtlen:
                    self._iterator = 0
            lcd.print(chunk, self.x, self.y, self.color)
        else:
            lcd.print(text, self.x, self.y, self.color)
            
    def stop(self):
        self.timer.deinit()

#remove the lines bellow if you want to use this as a class
def UISetup():
    lcd.setRotation(3)
    lcd.clear()
    lcd.font(lcd.FONT_UNICODE)

UISetup()
t = Ticker("This is a very long text", 0xffffff, sliding=False, delay=2)
tt = Ticker("The line can be longer and can go faster and can even have unicodэ symbols", 0x85fa92, y=20, speed=100, delay=10)
