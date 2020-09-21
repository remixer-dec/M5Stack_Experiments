import fire_module as fire
from m5stack import lcd
from random import randint
import time

w = 80
h = 160

fire.setup()
lcd.clear()

@micropython.viper
def render(w:int, h:int):
    for y in range(0, h-1):
        for x in range(0, w):
            clr = int(fire.fire(randint(0,254), x, y))
            if clr == 0:
                pass
            else:
                lcd.drawPixel(x, y, clr)

@micropython.viper
def drawLoop():
    while True:
        #start = int(time.ticks_ms())
        render(int(w), int(h))
        #end = int(time.ticks_ms())
        #print(end - start) #frametime
drawLoop()        