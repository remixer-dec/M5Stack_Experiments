# Maps for m5stickC
Simple maps app that lets you explore the world map, find specific locations and locate the device using nearest wifi data.  
![Demo](https://i.imgur.com/8oPkTzI.jpg)

This app is using [OpenStreetMaps](https://www.openstreetmap.org/copyright "OpenStreetMaps") API to find location by name, [MapBox](https://mapbox.com "MapBox") and [Yandex](https://yandex.com/dev/maps/staticapi/doc/1.x/dg/concepts/input_params-docpage/ "Yandex") for map tile images and [Mozilla Location Services](https://location.services.mozilla.com "Mozilla Location Services") for wifi based positioning.  
You need to set up MapBox API token before using the app, you can get one [here](https://www.mapbox.com/maps/satellite/#the-data), by clicking "start building". Or you can change map provider to Yandex, by editing the configuration ```USE_YANDEX = True```

### Requirements
This project requires the following external modules:
[mpy-img-decoder](https://github.com/remixer-dec/mpy-img-decoder) - custom PNG decoder that supports showing files without writing them to flash  
[accelKeyboard](https://github.com/remixer-dec/M5Stack_Experiments/tree/master/M5StickC/UIFlow/AccelerometerKeyboard) - a QWERTY keyboard module that uses accelerometer to input location  
[wifi](https://github.com/remixer-dec/M5Stack_Experiments/blob/master/M5StickC/UIFlow/TwitchClient/wifi.py) - a simple module to connect to a wifi network, can be replaced with similar built-in UIFlow functionality.  

### RAM issues:
If you face any memory-related problems, try decreasing map image height. Another solution would be to save PNG directly to flash and use native PNG renderer. Any optimization solutions are welcome.
  
### geolocate.py 
This file can be used as a library to get current device location coordinates using wifi data with ```findDevice()``` function, or to get coordinates of a place by its name using ```findPlace(name)``` function. 
