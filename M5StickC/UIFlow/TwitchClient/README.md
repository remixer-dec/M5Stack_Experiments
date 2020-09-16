# Experimental twitch.tv client for m5stickC
![Demo](https://i.imgur.com/rkXi9tf.gif)  
### What can you do with it?  
* browse top streams and games
* preview their image, channel name and viewer count
* join selected or entered chat room and read chat messages
### What can't you do with it? 
* play streams and videos
* view emotes in the chat


## Configuration

*you have to add a clientID to use this project, you can get it [here](https://dev.twitch.tv/console/apps/create) or [find](https://github.com/search) one ;)*  

Configuration is stored in ```tcfg``` dictionary.  
**clientID** - (str) twitch client ID  
**tickers** - (bool) uses tickers to scroll each line horizontally, othervise scrolls all messages vertically.  
**textBG** - (int or False), text color used as a background color of channel/game name text, works weird with UIFlow auto line-breaks  
  
### This project requires the following external modules:
  [mpy-img-decoder](https://github.com/remixer-dec/mpy-img-decoder) - custom jpeg decoder that supports showing files without saving them  
  [ticker](https://github.com/remixer-dec/M5Stack_Experiments/tree/master/M5StickC/UIFlow/Ticker) - a ticker library for multi-line scrolling chat  
  [accelKeyboard](https://github.com/remixer-dec/M5Stack_Experiments/tree/master/M5StickC/UIFlow/AccelerometerKeyboard) - a QWERTY keyboard module that uses accelerometer to input channel name  
  [uwebsockets](https://github.com/adrianalin/uwebsockets/tree/1977d95c06052ad9b77e22d07994921374f49d36/uwebsockets) - a websocket client to connect to chat servers, should be placed in uwebsockets folder   

### and includes the following modules:
  ```wifi.py``` - a simple module to connect to a wifi network, can be replaced with similar built-in UIFlow functionality  
  ```selectionManager.py``` - a module to make menu item selection interfaces, similar to UIFlow built-in menu.  
    
Twitch is a Trademark by Twitch Interactive, Inc