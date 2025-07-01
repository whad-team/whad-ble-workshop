#!/usr/bin/python3

from whad.ble import Central, Scanner
from whad.ble.profile import UUID
from whad.device import WhadDevice
from whad.ble.stack.att.exceptions import InsufficientAuthenticationError
import sys, datetime, time
from struct import pack, unpack
from queue import Queue
import argparse
from whad.common.monitors import WiresharkMonitor


def display_help():
    print("[i] Available commands: ")
    print("\t- wireshark [start|stop]: start or stop wireshark")
    print("\t- name: get device name")
    print("\t- locate: locate the track")
    print("\t- mail <message>: Send a mail notification")  
    print("\t- quit: disconnect and exit the client")
    

class ZeTrackClient:
    def __init__(self, iface):

        self.monitor = WiresharkMonitor()
        self.connector = Central(WhadDevice.create(iface))
        self.monitor.attach(self.connector)
        self.monitored  = False

        self.address = None
        self.random = None
        self.device = None

        self.cmd_charac = None
        self.response_charac = None
        self.response_queue = Queue()

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

        self.device = self.connector.connect(self.address, random=True, hop_interval=52)
        try:
            self.device.discover()
        except InsufficientAuthenticationError:
            pass

        self.cmd_charac = self.device.find_characteristic_by_uuid(UUID(0x0002))
        self.response_charac = self.device.find_characteristic_by_uuid(UUID(0x0003))

        if self.response_charac.can_notify():
            if self.response_charac.subscribe(notification=True, callback=self.notification_callback):
                return True # print(f"Succesfully subscribed for notifications.")
            else:
                return False # print(f"An error occured while subscribing for notifications.")
        
        
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
                if device.name is not None and "ZeTrack" in device.name:
                    print(device.name, ": ", device.address)
                    addresses += [device.address]

        except KeyboardInterrupt:
            scanner.close()
        return addresses

    def send_command(self, opcode, payload):
        if self.cmd_charac is not None:
            self.cmd_charac.write(pack('B', opcode) + payload, without_response=True)
            return True
        return False

    def wait_response(self, filter_func):
        while not self.response_queue.empty():
            resp = self.response_queue.get()
            if filter_func(resp):
                return resp

        return None

    
    def send_notification(self, sender, message, icon=6):
        self.send_command(0xd8, b"\x00")
        split_phase_1 = []
        
        while len(sender) > 0x0e:
            split_phase_1.append(sender[:0x0e])
            sender = sender[0x0e:]
        split_phase_1.append(sender)

        split_phase_2 = []
        
        while len(message) > 0x0e:
            split_phase_2.append(message[:0x0e])
            message = message[0x0e:]
        split_phase_2.append(message)

        count = 1
        for chunk in split_phase_1 + split_phase_2:
            cmd = (
                pack('B', icon) + 
                pack('B', len(chunk)) + 
                pack('B', len(split_phase_1) + len(split_phase_2)) + 
                pack('B', count) +
                pack('B', 0x02) + 
                chunk.encode('ascii')
            )
            count += 1
            self.send_command(0xc2, cmd)

    def set_watchface(self, face):
        if face < 0 or face > 4:
            return False
        else:
            return self.send_command(0xc7, pack('B', face) + bytes.fromhex("000000000000000000000000000000000000"))

    def get_firmware_version(self):
        self.send_command(0xA1, bytes.fromhex("00000007e9061e151a08010104000000000000"))
        resp = self.wait_response(lambda resp:resp[0] == 0xA1)
        if resp is not None:
            return (resp[6], resp[7], resp[8])
        else:
            return (0xFF, 0xFF, 0xFF)
            
    def generate_command(self, type, opcode, payload):
        cmd = (
            b"\xab\x00\x00" + 
            pack('B', 4 + len(payload)) + 
            pack('I', 0) + 
            pack('<H', type) + 
            pack('<H', opcode) + payload
        )
        chunks = []
        while len(cmd) > 20:
            chunks.append(cmd[:20])
            cmd = cmd[20:]
        chunks.append(cmd)
        return chunks

    def send_command(self, type, opcode, payload):
        for chunk in self.generate_command(type, opcode, payload):
            self.cmd_charac.write(chunk, without_response=True)


    def locate(self):
        self.send_command(1, 0x18, b"\x00")

    def send_mail(self, message):
        self.send_command(2, 0x14,  b"\x30" + pack('B', len(message)) + message.encode('ascii'))


    def notification_callback(self, characteristic, value: bytes, indication=False):
        if characteristic.uuid == UUID(0x0003):
            print("[notif] ", value)
            self.response_queue.put(value)
        
parser = argparse.ArgumentParser()
                    
parser.add_argument("-a", "--address", help="connect to the target device",
                    default=None)
                    
parser.add_argument("-i", "--interface", help="interface to use",
                    default="hci0")

args = parser.parse_args()
interface = args.interface

if args.address is None:
    ZeTrackClient.scan(interface)
else:
    client  = ZeTrackClient(interface)
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

                    elif verb == "name":
                        print("[i] Device name: ", client.get_device_name())

                    elif verb == "locate":
                        client.locate()

                    elif verb == "mail":
                        if len(word) < 2:
                            print("[i] Enter message.")
                        else:
                            client.send_mail(" ".join(word[1:]))

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