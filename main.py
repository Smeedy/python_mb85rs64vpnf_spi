from machine import SPI
from mb85rs64vpnf_spi import MB85RS64VPNF_SPI
import logging

logging.basicConfig(level=logging.DEBUG)

# soft SPI
#spi = SPI(0, mode=SPI.MASTER, baudrate=8000000, polarity=0, phase=0, pins=('P12','P11','P10'))

# configure the SPI master @ 2MHz
# this uses the Pycom LoPy hw SPI default pins for CLK, MOSI and MISO (``P10``, ``P11`` and ``P14``)
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
print(fram.read(0x0030, 14))
# bytearray(b'\xffHello, world!')
