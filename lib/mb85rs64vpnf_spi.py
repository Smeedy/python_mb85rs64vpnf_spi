######
#
#   mb85rs64vpnf_spi.py
#
#   Author: M. Smit (@smeedybuild1970), Oblivion BV.
#   License: GPLv3
#   Version: 1
#
#   --
#   Python library for reading and writing to FRAM memory with SPI
#   using a Fujitsu MB85RS64VPNF module.
#   --
#
#   You will need an SPI object (from hardware or soft-pin) for data transfer,
#   and a CS-pin (output) to activate/deactive the chip.
#
#   Credit where credit is due: This library is a plain and rather
#   straighforward port of the Adafruit CPP module (BSD) by
#   Kevin (KTOWN) Townsend for Adafruit Industries.
#
#   Adafruit invests time and resources providing this open source code,
#   please support Adafruit and open-source hardware by purchasing products
#   from Adafruit!
#
#   https://github.com/adafruit/Adafruit_FRAM_SPI.
#
#
#
#   Basic python usage:
#   ---
#
#   from mb85rs64vpnf_spi import MB85RS64VPNF_SPI
#
#   spi = SPI(0, mode=SPI.MASTER, baudrate=2000000, polarity=0, phase=0)
#   cs = machine.Pin('P12', machine.Pin.OUT)
#   fram = MB85RS64VPNF_SPI(spi, cs)
#
#   fram.writeEnable(True)
#   fram.write8(0x0030, 0xff)
#   fram.writeEnable(False)
#   print(fram.read8(0x0030))
#   # b'\xff'
#
#   fram.writeEnable(True)
#   fram.write(0x0031, "Hello, world!")
#   fram.writeEnable(False)
#   fram.read(0x0030, 14)
#   # bytearray(b'\xffHello, world!')
#

import logging # std micropython lib
from machine import SPI
#import struct



class MB85RS64VPNF_SPI:

    # constants
    OPCODE_WREN   = 0b0110      # Write Enable Latch
    OPCODE_WRDI   = 0b0100      # Reset Write Enable Latch
    OPCODE_RDSR   = 0b0101      # Read Status Register
    OPCODE_WRSR   = 0b0001      # Write Status Register
    OPCODE_READ   = 0b0011      # Read Memory
    OPCODE_WRITE  = 0b0010      # Write Memory
    OPCODE_RDID   = 0b10011111  # Read Device ID

    def __init__(self, spi, cs, address_size_bytes = 2, logging_level = logging.INFO):

        self._log = logging.getLogger('mb85rs64vpnf.MB85RS64VPNF')

        if spi is None or cs is None:
            raise ValueError('both spi and cs must be set')

        self._spi = spi
        self._cs = cs

        self._framInitialised = False
        if address_size_bytes > 4:
            raise ValueError('address_size_bytes must be <= 4')
        self._nAddressSizeBytes = address_size_bytes

        self._cs.value(1) # we start at high

        manufID, prodID = self.getDeviceID()
        self._log.debug('manufID: {}, prodID: {}'.format(manufID, prodID))

        if manufID != b'\x04' and manufID != b'\x07':
            raise ValueError('unknown manufID: {}'.format(manufID))

        if prodID != b'\x03\x02' and prodID != b'\x7f\x7f':
            raise ValueError('unknown prodID: {}'.format(prodID))

        self._framInitialised = True # somewhat useless now


    # /**************************************************************************/
    # /*!
    #     @brief  Enables or disables writing to the SPI flash
    #
    #     @params[in] enable
    #                 True enables writes, false disables writes
    # */
    # /**************************************************************************/
    def writeEnable (self, enable):

        self._cs.value(0)
        if enable:
            self._spi.write(self.OPCODE_WREN)
        else:
            self._spi.write(self.OPCODE_WRDI)
        self._cs.value(1)


    # /**************************************************************************/
    # /*!
    #     @brief  Writes a byte at the specific FRAM address
    #
    #     @params[in] addr
    #                 The 32-bit address to write to in FRAM memory
    #     @params[in] i2cAddr
    #                 The 8-bit value to write at framAddr
    # */
    # /**************************************************************************/
    def write8 (self, addr, value):

        self._cs.value(0)
        self._spi.write(self.OPCODE_WRITE)
        self._writeAddress(addr)
        self._spi.write(value)
        # /* CS on the rising edge commits the WRITE */
        self._cs.value(1)

    # /**************************************************************************/
    # /*!
    #     @brief  Writes count bytes starting at the specific FRAM address
    #
    #     @params[in] addr
    #                 The 32-bit address to write to in FRAM memory
    #     @params[in] values
    #                 The array of 8-bit values to write starting at addr
    # */
    # /**************************************************************************/
    def write (self, addr, values):

        self._cs.value(0)
        self._spi.write(self.OPCODE_WRITE)
        self._writeAddress(addr)
        for value in values:
            self._spi.write(value)
        # /* CS on the rising edge commits the WRITE */
        self._cs.value(1)

    # /**************************************************************************/
    # /*!
    #     @brief  Reads an 8 bit value from the specified FRAM address
    #
    #     @params[in] addr
    #                 The 32-bit address to read from in FRAM memory
    #
    #     @returns    The 8-bit value retrieved at framAddr
    # */
    # /**************************************************************************/
    def read8 (self, addr):

        self._log.debug('[read8] read 1 byte')

        self._cs.value(0)
        self._spi.write(self.OPCODE_READ)
        self._writeAddress(addr)
        data = self._spi.read(1)
        self._cs.value(1)

        return data

    # /**************************************************************************/
    # /*!
    #     @brief  Read count bytes starting at the specific FRAM address
    #
    #     @params[in] addr
    #                 The 32-bit address to write to in FRAM memory
    #     @params[in] count
    #                 The number of bytes to read
    #     @returns    data
    #                 The pointer to an array of 8-bit values to read starting at addr
    # */
    # /**************************************************************************/
    def read (self, addr, count):

        self._log.debug('[read] reading {} bytes'.format(count))
        data = bytearray()

        self._cs.value(0)
        self._spi.write(self.OPCODE_READ)
        self._writeAddress(addr)
        for _ in range(count):
            data.extend(self._spi.read(1))
        self._cs.value(1)

        return data


    # /**************************************************************************/
    # /*!
    #     @brief  Reads the Manufacturer ID and the Product ID from the IC
    #
    #     @params[out]  manufacturerID
    #                   The 8-bit manufacturer ID (Fujitsu = 0x04)
    #     @params[out]  productID
    #                   The memory density (bytes 15..8) and proprietary
    #                   Product ID fields (bytes 7..0). Should be 0x0302 for
    #                   the MB85RS64VPNF-G-JNERE1.
    # */
    # /**************************************************************************/
    def getDeviceID(self):

        self._cs.value(0)
        self._spi.write(self.OPCODE_RDID)
        data = self._spi.read(4)
        self._cs.value(1)

        self._log.debug('[getDeviceID] data: {}'.format(data))
        # /* Slice values to separate manuf and prod IDs */
        # /* See p.10 of http://www.fujitsu.com/downloads/MICRO/fsa/pdf/products/memory/fram/MB85RS64V-DS501-00015-4v0-E.pdf */
        return data[0:1], data[2:4]

    # /**************************************************************************/
    # /*!
    #     @brief  Reads the status register
    # */
    # /**************************************************************************/
    def getStatusRegister(self):

        self._cs.value(0)
        self._spi.write(self.OPCODE_RDSR)
        data = self._spi.read(1)
        self._cs.value(1)

        return data

    # /**************************************************************************/
    # /*!
    #     @brief  Sets the status register
    # */
    # /**************************************************************************/
    def setStatusRegister(self, value):

        self._cs.value(0)
        self._spi.write(self.OPCODE_WRSR)
        self._spi.write(value)
        data = self._spi.read(1)
        self._cs.value(1)


    def _writeAddress(self, addr):
        """Sets the correct address depending on the address size."""

        self._log.debug('[_writeAddress] addr: {}'.format(addr))

        if self._nAddressSizeBytes > 3:
            self._spi.write(addr >> 24)
        if self._nAddressSizeBytes > 2:
            self._spi.write(addr >> 16)
        self._spi.write(addr >> 8)
        self._spi.write(addr & 0xFF)


    # def _reverse(self, bytes):
    #     return struct.pack('<2h', *struct.unpack('>2h', bytes))
