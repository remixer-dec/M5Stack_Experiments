from m5stack import lcd, btnA, btnB

class SelectionManager:
    def __init__(self, total, boxW=80, boxH=20, boxColor = 0xffffff, bgColor=0, offsetY=0, callback=print, menu=0):
        self.total = total + menu
        self.real = total
        self.boxW = boxW
        self.boxH = boxH
        self.boxColor = boxColor
        self.bgColor = bgColor
        self.offsetY = offsetY
        self.selection = 1
        self.callback = callback

    def loop(self):
        self._render()
        while btnA.isPressed():
            pass
        while True:
            if btnB.isPressed():
                self.selection = (self.selection + 1) if self.selection < self.total else 1
                while True:
                    if not btnB.isPressed():
                        break
                self._render()
            if btnA.isPressed():
                return self.callback(self.selection - 1)

    def _render(self):
        def selOffset(selection):
            selection = selection if selection > 0 else self.real
            return (self.offsetY + (selection - 1) * self.boxH)
        if self.selection > self.real:
            if self.selection % 2 == 0:
                lcd.drawRect(0, selOffset(self.selection - 1), self.boxW, self.boxH, self.bgColor)
                lcd.drawRect(0, 144, 40, 16, self.boxColor)
            else:
                lcd.drawRect(0, 144, 40, 16, self.bgColor)
                lcd.drawRect(40, 144, 40, 16, self.boxColor)
        else:
            if self.selection == 1:
                lcd.drawRect(40, 144, 40, 16, self.bgColor)
            lcd.drawRect(0, selOffset(self.selection - 1), self.boxW, self.boxH, self.bgColor)
            lcd.drawRect(0, selOffset(self.selection), self.boxW, self.boxH, self.boxColor)
