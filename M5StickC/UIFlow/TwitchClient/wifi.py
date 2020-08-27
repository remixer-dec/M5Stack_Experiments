import network
import time

wlan=None

def connect(ssid = "YOUR_WIFI_SSID", passwd = "YOUR_WIFI_PASS"):
  global wlan
  wlan=network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.disconnect()
  wlan.connect(ssid, passwd)

  while(wlan.ifconfig()[0] == '0.0.0.0'):
    time.sleep(1)
  return True
