#!/usr/bin/env python3

from whad.ble import Central, Scanner
from whad.ble.profile import UUID
from whad.device import WhadDevice
import sys, datetime, time
from struct import pack, unpack
from queue import Queue
import argparse
from whad.common.monitors import WiresharkMonitor
from scapy.layers.bluetooth import ATT_Handle_Value_Notification

def display_help():
    print("[i] Available commands: ")
    print("\t- wireshark [start|stop]: start or stop wireshark")
    print("\t- start_alert: start the immediate alert")
    print("\t- stop_alert: stop the immediate alert")
    print("\t- wait_press: wait until a keypress is received")
    print("\t- quit: disconnect and exit the client")
    

class ITagClient:
    def __init__(self, iface):
        self.monitor = WiresharkMonitor()
        self.connector = Central(WhadDevice.create(iface))
        self.monitor.attach(self.connector)
        self.monitored = False
        self.address = None
        self.random = None
        self.device = None
        self.press = False
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


    def connect(self, address, random=False):
        self.address = address
        self.random = random

        self.device = self.connector.connect(self.address, random=self.random)

        self.device.discover()
        self.alert_charac = self.device.get_characteristic(UUID(0x1802), UUID(0x2A06))
        self.connector.attach_callback(self.notification_callback, on_reception=True)
        return True
        '''
        self.trigger_charac = self.device.get_characteristic(UUID(0xFFE0), UUID(0xFFE1))
        
        if self.trigger_charac is not None and self.trigger_charac.can_notify():
            if self.trigger_charac.subscribe(notification=True, callback=self.notification_callback):
                return True
            else:
                return False
        '''
    def wait_press(self):
        self.press = False
        while not self.press:
            time.sleep(1)
        
        return True

    def disconnect(self):
        if self.device is not None:
            self.device.disconnect()
        if self.monitored:
            self.monitor.close()
        if self.connector is not None:
            self.connector.close()

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
                if device.name is not None and "iTAG" in device.name:
                    print(device.name, ": ", device.address)
                    addresses += [device.address]

        except KeyboardInterrupt:
            scanner.close()
        return addresses


    def trigger_alert(self, enable=True):
        if enable:
            self.alert_charac.write(b"\x01", without_response=True)
        else:
            self.alert_charac.write(b"\x00", without_response=True)
            
        return None


    def notification_callback(self, pkt):
        if ATT_Handle_Value_Notification in pkt:
            self.press = True
        
parser = argparse.ArgumentParser()
                    
parser.add_argument("-a", "--address", help="connect to the target device",
                    default=None)
                    
parser.add_argument("-i", "--interface", help="interface to use",
                    default="hci0")

args = parser.parse_args()
interface = args.interface

if args.address is None:
    ITagClient.scan(interface)
else:
    client  = ITagClient(interface)
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

                    elif verb == "start_alert":
                        print("[i] Starting alert.")
                        client.trigger_alert(True)

                    elif verb == "stop_alert":
                        print("[i] Stopping alert.")
                        client.trigger_alert(False)

                    elif verb == "wait_press":
                        print("[i] Waiting for keypress...")
                        if client.wait_press():
                            print("[i] Keypress received !")

                    elif verb == "name":
                        print("[i] Device name: ", client.get_device_name())

                    elif verb == "help":
                        display_help()
                    elif verb == "quit":
                        exit(0)
                    else:
                        print("[i] Unknown command.")
            except KeyboardInterrupt:
                exit(0)

            except Exception as e:
                print("[i] Unknown command.")
                print(e)