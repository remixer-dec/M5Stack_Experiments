## IP Camera PoC
  
The idea is to capture images using UnitV camera, transfer them to StickC via UART and make the live-stream accessible via built-in web server.  
This project was only developed as proof-of-concept and should not be used in production. The main bottleneck is StickC's RAM. A better  solution would be to create a custom web server, which sends image parts to client, as soon as they're received in UART.
![Demo](https://i.imgur.com/VAwg6l2.png)  
### Frontend
The frontend app can be used to watch the livestream, configure basic camera settings and set up some post-processing jobs. It can be laucnhed from device's server direcrly, or can be placed to external server instead. Make sure to add ```<base href='YOUR_M5STICKC_IP'>``` inside the head tag, to place it somewhere else.
  
#### Setup
This app uses external [wifi](https://github.com/remixer-dec/M5Stack_Experiments/blob/master/M5StickC/UIFlow/TwitchClient/wifi.py) module - a simple silent module to connect to a wifi network. It can be replaced with similar built-in UIFlow functionality.  
To provide some basic security, the server has a whitelist function that is used as a decorator to filter requests by IP and allow only ones from the list. Add your IPs to the list or remove all ```whitelist``` decorators if you don't want to use it.  
Don't forget to put index.html to /flash/www/  
Finally, 3 easy steps to launch the app:  
1) run [UnitV code](https://github.com/remixer-dec/M5Stack_Experiments/blob/master/UnitV/MaixPy/IPCamera)  
2) run StickC code  
3) navigate to StickC's IP  
    