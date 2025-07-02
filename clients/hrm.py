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
    print("\t- start: start heart rate monitoring")
    print("\t- stop: stop heart rate monitoring")
    print("\t- battery: display battery level")            
    print("\t- quit: disconnect and exit the client")
    

class HRMClient:
    def __init__(self, iface):
        self.monitor = WiresharkMonitor()
        self.connector = Central(WhadDevice.create(iface))
        self.monitor.attach(self.connector)
        self.monitored  = False

        self.address = None
        self.random = None
        self.device = None
        self.show = False
        self.alert_charac = None

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

    def connect(self, address, random=True):
        self.address = address
        self.random = random

        self.device = self.connector.connect(self.address, random=self.random, hop_interval=56)

        self.device.discover()

        self.firmware_charac = self.device.find_characteristic_by_uuid(UUID(0x2A26))
        self.hrm_charac = self.device.find_characteristic_by_uuid(UUID(0x2A37))
        self.battery_charac = self.device.find_characteristic_by_uuid(UUID(0x2a19))

        return self.hrm_charac is not None
        
    def disconnect(self):
        if self.device is not None:
            self.device.disconnect()
        if self.monitored:
            self.monitor.close()
        if self.connector is not None:
            self.connector.close()


    def get_firmware_version(self):
        value = self.firmware_charac.value
        if value is not None:
            return value

    def get_battery(self):
        value = self.battery_charac.value
        if value is not None:
            return value[0]

    def get_device_name(self):
        if self.device is not None:
            device_name = self.device.get_characteristic(UUID(0x1800), UUID(0x2A00))
            return device_name.value
        return None
    
    @classmethod
    def scan(cls, iface):
        scanner = Scanner(WhadDevice.create(iface))
        scanner.start()
        addresses = []
        try:
            for device in scanner.discover_devices():
                if device.name is not None and "HR" in device.name:
                    print(device.name, ": ", device.address)
                    addresses += [device.address]

        except KeyboardInterrupt:
            scanner.close()
        return addresses


    def start_measures(self):
        self.show = True
        if self.hrm_charac.can_notify():
            if self.hrm_charac.subscribe(notification=True, callback=self.notification_callback):
                return True
            else:
                return False
                

    def stop_measures(self):
        self.show = False
        if self.hrm_charac.can_notify():
            if self.hrm_charac.unsubscribe():
                return 
            else:
                return False
                


    def notification_callback(self, characteristic, value: bytes, indication=False):
        if self.show and characteristic.uuid == UUID(0x2a37):
            sys.stdout.write("\r[["+ str(self.address) + " | " + str(value[1]) + " bpm" +  "]] ~> ")
            sys.stdout.flush()
        
parser = argparse.ArgumentParser()
                    
parser.add_argument("-a", "--address", help="connect to the target device",
                    default=None)
                    
parser.add_argument("-i", "--interface", help="interface to use",
                    default="hci0")

args = parser.parse_args()
interface = args.interface

if args.address is None:
    HRMClient.scan(interface)
else:
    client  = HRMClient(interface)
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

                    elif verb == "start":
                        print("[i] Starting HR monitoring, enter stop to stop.")
                        client.start_measures()

                    elif verb == "stop":
                        print("[i] Stopping HR monitoring.")
                        client.stop_measures()

                    elif verb == "battery":
                        value = client.get_battery()
                        if value is not None:
                            print("[i] Battery level: ", value, "%")

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
                print(e)