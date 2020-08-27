from m5stack import lcd, btnA, btnB


class Keyboard:
    def __init__(self, cursorSize=4, sensitivity=0.6, cursorColor=0x11f011, topBG=0, keyboardBG=0x444444, textColor = 0xffffff):
        self.input = ''
        self.cursorSize = cursorSize
        self.sensitivity = sensitivity
        self.cursorColor = cursorColor
        self.topBG = topBG
        self.keyboardBG = keyboardBG
        self.textColor = textColor
        lcd.clear()
        lcd.font(lcd.FONT_Small)

    def loop(self):
        from hardware import mpu6050
        mpu = mpu6050.MPU6050()
        maxX = 80.0
        maxY = 160.0
        accel = [0.0, 0.0]
        accelSense = self.sensitivity
        curSize = self.cursorSize
        curPos = [40.0, 40.0]
        self._drawInputForm()
        self._drawLayoutBG()
        while True:
            self._showLayout()
            self._drawSelectedLetter(curPos)
            if curPos[1] <= 21:
                self._drawInputForm()
                self._drawInputText()
            accelX = mpu.acceleration[0] * accelSense * -1
            accelY = mpu.acceleration[1] * accelSense
            lcd.fillRect(round(curPos[0]), round(curPos[1]), curSize, curSize,
                         self.topBG if curPos[1] < 104 else self.keyboardBG)
            if curPos[0] + accelX < 80 - curSize and curPos[0] + accelX > 0:
                curPos[0] += accelX
            if curPos[1] + accelY < 160 - curSize and curPos[1] + accelY > 0:
                curPos[1] += accelY
            lcd.fillRect(round(curPos[0]), round(curPos[1]), curSize, curSize,
                         self.cursorColor)
            if btnA.isPressed():
                key = self._getLetter(curPos)
                if key == '>':
                    self._hide()
                    return self.input
                else:
                    self.input += key
                    self._drawInputText()
                while btnA.isPressed():
                    pass
            if btnB.isPressed():
                if len(self.input) > 0:
                    self.input = self.input[:-1]
                    self._drawInputText()
                while btnB.isPressed():
                    pass

    def _drawInputText(self):
        lcd.fillRect(10, 10, 90, 10, self.topBG)
        txt = self.input if len(self.input) < 8 else ('~' + self.input[-7:])
        lcd.print(txt, 10, 9, self.textColor)

    def _drawInputForm(self):
        lcd.drawLine(10, 20, 70, 20, self.textColor)

    def _drawSelectedLetter(self, curPos):
        lcd.fillRect(0, 92, 11, 11, self.topBG)
        lcd.print(self._getLetter(curPos), 0, 92, self.cursorColor)

    def _drawLayoutBG(self):
        for i in range(56):
            lcd.fillRect(0, 160 - i, 80, 160, self.keyboardBG)
        return self

    def _showLayout(self):
        lcd.fillRect(0, 104, 80, 4, self.keyboardBG)
        lcd.print('123456789', 0, 108, self.textColor)
        lcd.print('0', 71, 108, self.textColor)
        lcd.print('QWERTYUIO', 0, 120, self.textColor)
        lcd.print('P', 71, 120, self.textColor)
        lcd.print('ASDFGHJKL', 0, 132, self.textColor)
        lcd.print('-', 71, 132, self.textColor)
        lcd.print('ZXCVBNM._', 0, 144, self.textColor)
        lcd.drawLine(78, 148, 78, 152, self.textColor)
        lcd.drawLine(78, 152, 74, 152, self.textColor)
        return self

    def _hide(self):
        for i in range(68):
            lcd.fillRect(0, 90, 80, 3 + i, self.topBG)

    def _getLetter(self, pos):
        x, y = pos
        l = ''
        if y < 108:
            return ''
        if y < 120:
            return '1234567890'[round(x / 80 * 10)]
        if y < 132:
            return 'QWERTYUIOP'[round(x / 80 * 10)]
        if y < 144:
            return 'ASDFGHJKL-'[round(x / 80 * 10)]
        if y < 160:
            return 'ZXCVBNM._>'[round(x / 80 * 10)]

#k = Keyboard().loop()