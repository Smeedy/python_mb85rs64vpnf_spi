# python_mb85rs64vpnf_spi

Author: M. Smit (@smeedybuild1970)  
License: GPLv3  
Version: 1  

Python library for reading and writing to FRAM memory with SPI using a Fujitsu
MB85RS64VPNF module. You will need an SPI object (from hardware or soft-pin) for
data transfer, and a CS-pin (output) to activate/deactive the chip.

## Adafruit
Credit where credit is due: This library is a plain and rather
straighforward port of the Adafruit CPP module (BSD) by
Kevin (KTOWN) Townsend for Adafruit Industries.

Adafruit invests time and resources providing this open source code,
please support Adafruit and open-source hardware by purchasing products
from Adafruit!

[https://github.com/adafruit/Adafruit_FRAM_SPI](https://github.com/adafruit/Adafruit_FRAM_SPI)

## Basic python usage:
```
from mb85rs64vpnf_spi import MB85RS64VPNF_SPI

spi = SPI(0, mode=SPI.MASTER, baudrate=2000000, polarity=0, phase=0)
cs = machine.Pin('P12', machine.Pin.OUT)
fram = MB85RS64VPNF_SPI(spi, cs)

fram.writeEnable(True)
fram.write8(0x0030, 0xff)
fram.writeEnable(False)
print(fram.read8(0x0030))
# b'\xff'

fram.writeEnable(True)
fram.write(0x0031, "Hello, world!")
fram.writeEnable(False)
data = fram.read(0x0030, 14)
# bytearray(b'\xffHello, world!')
```
