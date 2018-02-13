import machine
import os

# disable WiFi
from network import WLAN
wlan = WLAN()
wlan.deinit()

# disable bluetooth
from network import Bluetooth
bt = Bluetooth()
bt.deinit()

import pycom
pycom.heartbeat(False)

#machine.main('main.py')
