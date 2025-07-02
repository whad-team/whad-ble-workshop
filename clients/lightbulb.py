#!/usr/bin/env python3

from whad.ble import Central, Scanner
from whad.ble.profile import UUID
from whad.device import WhadDevice
import sys, datetime, time
from struct import pack, unpack
from queue import Queue
import argparse
from whad.common.monitors import WiresharkMonitor


def display_help():
    print("[i] Available commands: ")
    print("\t- wireshark [start|stop]: start or stop wireshark")
    print("\t- name: get device name")
    print("\t- firmware: get device firmware version")
    print("\t- on: turn bulb on")
    print("\t- off: turn bulb off")
    print("\t- brightnness [0-8]: configure brightness")
    print("\t- white: enter white mode")
    print("\t- color <red> <green> <blue>: enter color mode and set color")
    print("\t- quit: disconnect and exit the client")
    

class LighbulbClient:
    def __init__(self, iface):
        self.monitor = WiresharkMonitor()
        self.connector = Central(WhadDevice.create(iface))
        self.monitor.attach(self.connector)
        self.monitored  = False
        self.address = None
        self.random = None
        self.device = None
        
        self.firmware_charac = None 
        self.cmd_charac = None

    def wireshark(self, enable):
        if enable:
            if not self.monitored:
                self.monitor.start()
            self.monitored = True
        else:
            if self.monitored:
                self.monitor.close()
                self.monitor.detach()

                self.monitor = WiresharkMonitor()
                self.monitor.attach(self.connector)

            self.monitored = False

    def connect(self, address, random=False):
        self.address = address
        self.random = random

        self.device = self.connector.connect(self.address, random=self.random)

        self.device.discover()
        self.firmware_charac = self.device.find_characteristic_by_uuid(UUID(0x2A26))
        self.cmd_charac = self.device.find_characteristic_by_uuid(UUID("a8b3fff1-4834-4051-89d0-3de95cddd318"))
        return True
        
    def disconnect(self):
        if self.device is not None:
            self.device.disconnect()
        if self.monitored:
            self.monitor.close()
        if self.connector is not None:
            self.connector.close()

    def get_firmware_version(self):
        if self.device is not None:
            firmware_version = self.firmware_charac.value
            return firmware_version
        return None

    def get_device_name(self):
        if self.device is not None:
            device_name = self.device.get_characteristic(UUID(0x1800), UUID(0x2A00))
            return device_name.value
        return None
    
    def generate_command(self, opcode, payload):
        return pack('B', 0x55) + pack('B', opcode) + payload + b"\x0d\x0a"

    def write_command(self, opcode, payload):
        if self.cmd_charac is not None: 
            self.cmd_charac.write(self.generate_command(opcode, payload), without_response=True)   
            return True
        return False

    @classmethod
    def scan(cls, iface):
        scanner = Scanner(WhadDevice.create(iface))
        scanner.start()
        addresses = []
        try:
            for device in scanner.discover_devices():
                if device.name is not None and "74:da" in str(device.address):
                    print("Lightbulb: ", device.address)
                    addresses += [device.address]

        except KeyboardInterrupt:
            scanner.close()
        return addresses


    def on(self):
        self.write_command(0x10, b"\x01")


    def off(self):
        return self.write_command(0x10, b"\x00")


    def brightness(self, value):
        if value > 8 or value < 0:
            return False
            
        self.write_command(0x12, bytes([value+2]))

    def white(self):
        return self.write_command(0x14, b"\x80\x80\x80")


    def color(self, r, g, b):
        return self.write_command(0x13, bytes([r, g, b]))

    def notification_callback(self, characteristic, value: bytes, indication=False):
        print(characteristic, value)
        
parser = argparse.ArgumentParser()
                    
parser.add_argument("-a", "--address", help="connect to the target device",
                    default=None)
                    
parser.add_argument("-i", "--interface", help="interface to use",
                    default="hci0")

args = parser.parse_args()
interface = args.interface

if args.address is None:
    LighbulbClient.scan(interface)
else:
    client  = LighbulbClient(interface)
    if client.connect(args.address):
        print("[i] Connected to ", args.address, "!")    
        display_help()
        print()
        while True:
            try:
                print("[[", args.address, "]] ~> ", end="")
                word = input().split()
                if len(word) > 0:
                    verb = word[0]
                    if verb == "wireshark":
                        if len(word) != 2:
                            print("[i] Enter wireshark start / stop to start or stop wireshark.")
                        else:
                            if word[1] == "on" or word[1] == "start":
                                client.wireshark(True)

                            elif word[1] == "off" or word[1] == "stop":
                                client.wireshark(False)
                            else:
                                print("[i] Enter wireshark start / stop to start or stop wireshark.")

                    elif verb == "on":
                        client.on()

                    elif verb == "off":
                        client.off()
                    

                    elif verb == "white":
                        client.white()
                    
                    elif verb == "brightness": 
                        if len(word) == 2:
                            try:
                                bright = int(word[1])
                                client.brightness(bright)
                            except ValueError:
                                print("[i] Enter brightness between 0 and 8")
                        else:
                            print("[i] Enter brightness between 0 and 8")
                    elif verb == "color": 
                        if len(word) == 4:
                            try:
                                r = int(word[1])
                                g = int(word[2])
                                b = int(word[3])

                                client.color(r, g, b)

                            except ValueError:
                                print("[i] Please enter red, green and blue components (between 0 & 255).")
                        else:
                            print("[i] Please enter red, green and blue components (between 0 & 255).")
                    elif verb == "name":
                        print("[i] Device name: ", client.get_device_name())
                    elif verb == "firmware":
                        print("[i] Firmware version: ", client.get_firmware_version())

                    elif verb == "help":
                        display_help()
                    elif verb == "quit":
                        client.disconnect()
                        exit(0)
                    else:
                        print("[i] Unknown command.")
            except KeyboardInterrupt:
                client.disconnect()
                exit(0)

            except Exception as e:
                print("[i] Unknown command.")
                