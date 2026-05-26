#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import os
import sys
import time
import threading
from pathlib import Path

import pyftdi.serialext


class DmxPy:
    def __init__(self, serialPort, pro=True, path='dmxpy2.txt'):
        try:
            self.serial = pyftdi.serialext.serial_for_url(serialPort,
                                                          baudrate=250000,
                                                          stopbits=2)
        except pyftdi.serialext.SerialException:
            print("Error: could not open Serial Port")
            sys.exit(0)
        self.proModel: bool = pro
        self.dmx_size: int = 512
        if self.proModel:
            self.dmxData: list(int) = [0] + [0] * self.dmx_size
        else:
            self.dmxData: list(bytes) = [bytes([0])] + [bytes([0])] * self.dmx_size
        self.path: Path = Path.home() / path
        try:
            with open(self.path, 'x'):
                pass
            print("Created DMX file")
        except FileExistsError:
            print("DMX file exists")
        try:
            self.ftime: float = os.stat(self.path).st_ctime
        except OSError as e:
            print("No DMX file found, generating new one.")
            raise e

    def readFile(self):
        try:
            with open(self.path, 'r') as f:
                i: int = 0
                while True:
                    chars: str = f.read(2)
                    substr: str = chars.strip()
                    if not substr:
                        print('Reached end of file')
                        break
                    if not isHex(substr):
                        continue
                    i = i + 1
                    if i > 512:
                        break
                    if self.proModel:
                        self.dmxData[i] = int(substr, 16)
                    else:
                        self.dmxData[i] = bytes([int(substr, 16)])
        except OSError:
            print("No DMX cache file found. Initiate new channel array.")

    def setChannel(self, chan, intensity):
        if chan > 512:
            chan = 512
        if chan < 0:
            chan = 0
        if intensity > 255:
            intensity = 255
        if intensity < 0:
            intensity = 0
        self.dmxData[chan] = bytes([intensity])

    def blackout(self):
        for i in range(1, 512, 1):
            self.dmxData[i] = bytes([0])

    def render(self):
        if self.proModel:
            dmx_open: list(int) = [0x7E]
            dmx_close: list(int) = [0xE7]
            dmx_intensity: list(int) = [6, (self.dmx_size + 1) & 0xFF,
                                        (self.dmx_size + 1) >> 8 & 0xFF]
            self.serial.write(
                    bytearray(dmx_open + dmx_intensity + self.dmxData
                              + dmx_close))
        else:
            sdata: list(bytes) = b''.join(self.dmxData)
            self.serial.send_break(duration=0.001)
            self.serial.write(sdata)

    def display_universe(self):
        while True:
            if (self.ftime != os.stat(self.path).st_ctime):
                self.readFile()
                self.ftime = os.stat(self.path).st_ctime
            self.render()
            time.sleep(0.005)


def isHex(string):
    try:
        bytes.fromhex(string)
        return True
    except ValueError:
        return False


parser: ArgumentParser = ArgumentParser(
        description='Control Enttec DMX USB and Pro')
parser.add_argument('-s', '--serial', type=str, default='EN371065',
                    help='The serial number of the DMX USB device')
parser.add_argument('-p', '--pro', action='store_true',
                    help='Use the settings for the DMX USB Pro')
parser.add_argument('-c', '--cache', type=str, default='dmxpy2.txt',
                    help='The path relative to HOME to store the cache file')


args: Namespace = parser.parse_args()

# note device serial in the connect string
serial_address: str = 'ftdi://ftdi:232:' + args.serial + '/1'
dmx: DmxPy = DmxPy(serialPort=serial_address, pro=args.pro, path=args.cache)
dmx_thread = threading.Thread(target=dmx.display_universe)
dmx_thread.start()
