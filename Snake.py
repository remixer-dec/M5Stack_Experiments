# Created by remixer-dec and modify for M5stickC Plus2 by krkwsmk

from M5 import Lcd
from machine import Timer
from random import randint, seed
from utime import ticks_cpu
from hardware import *
    
class Food:
    pos = [0, 0]
    def generate():
        Food.pos = [randint(2, 237), randint(2, 131)]
        Food.pos = [Food.pos[0] if Food.pos[0] %2 == 0 else Food.pos[0] - 1, Food.pos[1] if Food.pos[1] % 2 == 0 else Food.pos[1] - 1]
        Food.checkPosition()
        
    def checkPosition():
        while Snake.tail.count(Food.pos) > 0:
            Food.generate()
 
class Snake:
    move_r = [2, 0]
    move_l = [-2,0]
    move_u = [0,-2]
    move_d = [0, 2]
    moves = [move_u, move_r, move_d, move_l]
    dr = 1 #direction
    tail = [[44, 44], [42, 44], [40, 44]]
    timer = Timer(58463)
    speed = 500
    notail = [2,2]
    isDead = False
    def isAlive(head):
        return head[0] > 0 and head[0] < 238 and head[1] > 0 and head[1] < 132 and Snake.tail.count(head) == 0
    
    def run():
        seed(ticks_cpu())
        Lcd.setRotation(3)
        Snake.timer.init(period=Snake.speed, mode=Timer.PERIODIC, callback=Snake.move)
        
    def dirChange():
        M5.update()
        if BtnB.wasPressed():
            Snake.dr += 1
        if BtnA.wasPressed():
            Snake.dr -= 1
        if Snake.dr > 3:
            Snake.dr = 0
        if Snake.dr < 0:
            Snake.dr = 3
            
    def reset():
        Snake.isDead = False
        Snake.tail = [[44, 44], [42, 44], [40, 44]]
        Snake.notail = [2,2]
        Snake.dr = 1
        Snake.speed = 500
        
    def speedUp():
        Snake.speed = Snake.speed - 20 if Snake.speed > 140 else 140
        Snake.timer.init(period=Snake.speed, mode=Timer.PERIODIC, callback=Snake.move)
        
    def move(tmr=None):
        head = Snake.tail[0].copy()
        Snake.dirChange()
        # Snake.basicAIMove(head) #uncomment this line if you want AI to play Snake
        head[0] += Snake.moves[Snake.dr][0]
        head[1] += Snake.moves[Snake.dr][1]
        if [head].count(Food.pos) == 0:
            Snake.notail = Snake.tail.pop() 
        else:
            Food.generate()
            Snake.speedUp()
        Snake.isDead = not Snake.isAlive(head)
        Snake.tail.insert(0, head)
        
    def basicAIMove(head):
        if head[0] == Food.pos[0]:
            Snake.dr = 2 if Food.pos[1] > head[1] and Snake.dr != 0 else 0 if Snake.dr !=2 else Snake.dr
        if head[1] == Food.pos[1]:
            Snake.dr = 1 if Food.pos[0] > head[0] and Snake.dr != 3 else 3 if Snake.dr !=1 else Snake.dr
        if (head[0] > 235 and Snake.dr == 1) or (head[0] < 3 and Snake.dr == 3):
            print(head[0])
            Snake.dr = 0 if head[1] > Food.pos[1] else 2
        if (head[1] > 129 and Snake.dr == 2) or (head[1] < 4 and Snake.dr == 0):
            Snake.dr = 3 if head[0] > Food.pos[0] else 1

class Game:
    def drawBorders():
        Lcd.drawRect(0, 1, 239, 133, 0xffd700)
        
    def prepareField():
        Snake.run()
        Lcd.clear()
        Game.drawBorders()
        Food.generate()
        
    def loop():
        #render snake
        for tailpart in Snake.tail:
            Lcd.fillRect(tailpart[0], tailpart[1], 2, 2)
        #clear old tail coords
        Lcd.fillRect(Snake.notail[0], Snake.notail[1], 2, 2, 0)
        #render food
        Lcd.fillRect(Food.pos[0], Food.pos[1], 2, 2, 0xffd700)
        return not Snake.isDead
    
    def over():
        Snake.timer.deinit()
        Lcd.clear()
        Lcd.setCursor(25, 40)
        Lcd.setTextSize(3)
        Lcd.print("GAME OVER")
        Lcd.setCursor(65, 70)
        Lcd.setTextSize(2)
        Lcd.print("Score: " + repr(len(Snake.tail)))
        while BtnA.wasPressed():
            pass
        while True:
            M5.update()
            if BtnA.wasPressed():
                Snake.reset()
                Game.prepareField()
                return 0

Game.prepareField()
while True:
    Game.loop() or Game.over()
