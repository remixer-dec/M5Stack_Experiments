## Accelerometer-controlled QWERTY keyboard for M5StickC with MPU6050 hardware  

![Demo](https://i.imgur.com/vmyJVCq.gif)
  
### Usage:
```python
from accelKeyboard import Keyboard
inputText = Keyboard().loop()
```

### Keyboard class
cursor size, accelerometer sensitivity, cursor color, screen background color, keyboard background color and text color are configurable in class constructor  
  
Keyboard layout was originally designed for [Twitch Client](https://github.com/remixer-dec/M5Stack_Experiments/tree/master/M5StickC/UIFlow/TwitchClient) channel search.  