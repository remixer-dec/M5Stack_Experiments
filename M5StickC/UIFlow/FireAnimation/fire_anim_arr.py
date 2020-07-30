from random import randint
from m5stack import lcd
import array
import time

w = 80
h = 160

@micropython.native
def hsl_to_rgb(HSLlist):
    H, S, L = HSLlist
    S = S/100
    L = L/100
    C = (1 - abs(2*L - 1)) * S
    X = C * (1 - abs(((H / 60) % 2)-1))
    m = L - C/2;
    [r1, g1, b1] = [C, X, 0] if H >= 0 and H < 60 else \
    [X, C, 0] if H >= 60 and H < 120 else \
    [0, C, X] if H >= 120 and H < 180 else \
    [0, X, C] if H >= 180 and H < 240 else \
    [X, 0, C] if H >= 240 and H < 300 else [C, 0, X]     
    return [int((r1 + m) * 255), int((g1 + m) * 255), int((b1 + m) * 255)]

@micropython.native
def rgb_to_int(RGBlist):
    r, g, b = RGBlist
    return (r << 0x10) + (g << 0x8) + b 

@micropython.native
def init():
    global fire, palette
    fire = [array.array('H', [0] * w) for x in range(0, h)]
    palette = [rgb_to_int(hsl_to_rgb([x // 3, 100, min(100, (x * 100 // 255) *2)])) for x in range(0, 255)]
        
@micropython.viper
def fireManager(fire, xo, yo, wo, ho):
    x = int(xo)
    y = int(yo)
    w = int(wo)
    h = int(ho)
    fire[y][x] = int(((\
              int(fire[(y + 1) % h][(x - 1 + w) % w]) \
            + int(fire[(y + 2) % h][(x) % w]) \
            + int(fire[(y + 1) % h][(x + 1) % w]) \
            + int(fire[(y + 3) % h][(x) % w])) * 64) // 257)
    

@micropython.viper
def render(fire, wo, ho):
    w = int(wo)
    h = int(ho)
    for x in range(0, w):
        fire[h-1][x] = randint(0,255)
    for y in range(0, h-1):
        for x in range(0, w):
            fireManager(fire, x, y, w, h)
            lcd.drawPixel(x, y, palette[int(fire[y][x])])

@micropython.viper
def renderer(fire):
    while 1:
        #start = int(time.ticks_us())
        render(fire, int(w), int(h))
        #end = int(time.ticks_us())
        #print(end - start) #frametime

init()
lcd.clear()    
renderer(fire)
