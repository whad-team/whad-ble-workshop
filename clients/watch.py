#!/usr/bin/python3

from whad.ble import Central, Scanner
from whad.ble.profile import UUID
from whad.device import WhadDevice
import sys, datetime
from struct import pack, unpack
from queue import Queue
import argparse
from whad.common.monitors import WiresharkMonitor


def display_help():
    print("[i] Available commands: ")
    print("\t- wireshark [start|stop]: start or stop wireshark")
    print("\t- id: get device ID")
    print("\t- firmware: get device firmware version")
    print("\t- pair: trigger pairing with device")
    print("\t- watchface [0-7]: Change watchface")
    print("\t- sms <sender> <message>: Send an SMS")            
    print("\t- quit: disconnect and exit the client")
    

class ZeCircleClient:
    def __init__(self, iface):
        self.monitor = WiresharkMonitor()
        self.connector = Central(WhadDevice.create(iface))
        self.monitor.attach(self.connector)
        self.monitored  = False
        self.address = None
        self.random = None
        self.device = None
        self.inbuff = None
        self.response_charac = None
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

    def connect(self, address, random=True):
        self.address = address
        self.random = random
        self.device = self.connector.connect(self.address, random=self.random)
        self.device.discover()
        
        self.cmd_charac = self.device.find_characteristic_by_uuid(UUID(0x8001))
        self.response_charac = self.device.find_characteristic_by_uuid(UUID(0x8002))

        self.response_queue = Queue()
        if self.response_charac.can_notify():
            if self.response_charac.subscribe(notification=True, callback=self.notification_callback):
                return True
            else:
                return False
                
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
                if device.name is not None and ("ZeFit" in device.name or "ZeCircle" in device.name):
                    print(device.name, ": ", device.address)
                    addresses += [device.address]

        except KeyboardInterrupt:
            scanner.close()
        return addresses

    def generate_command(self, opcode, payload):
        preamble = b"\x6f"
        postamble = b"\x8f"
        cmd = preamble + pack("<H", opcode)  + pack('<H', len(payload)) + payload + postamble
        
        cmds = []
        while len(cmd) > 20:
            chunk, cmd = cmd[:20], cmd[20:]
            cmds.append(chunk)
        
        cmds.append(cmd)
        
        return cmds

    def parse_response(self, response):
        # print("[rsp] ", response.hex())
        if response[0] == 0x6f and response[-1] == 0x8f:
            opcode = unpack('<H', response[1:3])[0]
            length = unpack('<H', response[3:5])[0]
            payload = response[5:-1]
            #print("\t", hex(opcode), payload)
            return opcode, length, payload

    def send_command(self, opcode, payload):
        if self.cmd_charac is not None:
            for chunk in self.generate_command(opcode, payload):

                self.cmd_charac.write(
                    chunk
                )
            self.response_charac.write(b"\x03", without_response=True)
            while self.response_queue.empty():
                pass
            return self.response_queue.get()
        return None

    def get_id(self):
        return self.send_command(0x7002, b"\x00")[2].decode('ascii')

    def get_firmware_version(self):
        return self.send_command(0x7003, b"\x01")[2].decode('ascii')

    def send_sms_v2(self, emetteur="Moi", message="ABCDABCD"):
        today = datetime.datetime.today()
        resp =  self.send_command(0x7176, 
            pack('<H', 0x1) + 
            pack('B', len(emetteur)) + 
            pack('B', len(message)) + 
            emetteur.encode('ascii') + 
            message.encode('ascii') + 
            today.strftime('%02Y%02m%02dT%02H%02M%02S').encode('ascii') + b"\x02\x01"
        )
        
        return resp

    def send_sms(self, emetteur="Moi", message="ABCDABCD"):
        today = datetime.datetime.today()
        resp =  self.send_command(0x7104, 
            pack('<H', today.year) + 
            pack('B', today.month) + 
            pack('B', today.day) + 
            pack('B',today.hour) + 
            pack('B',today.minute) + 
            pack('B', today.second) + b"\x00"
        )
        
        self.send_command(0x7171, b"\x00" + emetteur.encode('ascii'))
        self.send_command(0x7171, b"\x01" + message.encode('ascii'))
        self.send_command(0x7171, b"\x02" + today.strftime('%02Y%02m%02dT%02H%02M%02S').encode('ascii'))
        resp = self.send_command(0x7172, b"\x01\x60")
        return resp

    def pair(self):
        return self.send_command(0x7193, b"\x01")[2][-1] == 0

    def set_watchface(self, number):
        if number >= 0 and number <= 7:
            return self.send_command(0x7105, bytes.fromhex("06 01 01 00 01") +bytes([number]) + bytes.fromhex("00 00"))
        

    def notification_callback(self, characteristic, value: bytes, indication=False):
        if characteristic.uuid == UUID(0x8002):
            if value.startswith(b"\x6f"):
                self.inbuff = value
            else:
                self.inbuff += value
            if self.inbuff.endswith(b"\x8f"):
                self.response_queue.put(self.parse_response(self.inbuff))
                self.inbuff = None

parser = argparse.ArgumentParser()
                    
parser.add_argument("-a", "--address", help="connect to the target device",
                    default=None)
                    
parser.add_argument("-i", "--interface", help="interface to use",
                    default="hci0")

args = parser.parse_args()
interface = args.interface

if args.address is None:
    ZeCircleClient.scan(interface)
else:
    client  = ZeCircleClient(interface)
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

                    elif verb == "id":
                        print("[i] Client ID: ", client.get_id())
                    elif verb == "firmware":
                        print("[i] Firmware version: ", client.get_firmware_version())
                    elif verb == "pair":
                        if client.pair():
                            print("[i] Pairing successful.")
                        else:
                            print("[i] Pairing failed.")

                    elif verb == "watchface":
                        if len(word) != 2 or int(word[1]) < 0 or int(word[1]) > 7:
                            print("[i] Choose a facenumber between 0 & 7")
                        else:
                            facenumber = int(word[1])
                            if client.set_watchface(facenumber) is not None:
                                print("[i] Watchface succesfully updated !")
                            else:
                                print("[i] Watchface not updated.")

                    elif verb == "sms":
                        if len(verb) < 3:
                            print("[i] Enter sender and message.")
                        else:
                            sender = word[1]
                            message = " ".join(word[2:])
                            print("[i] Sender: ", sender, " | message: ", message)
                            if b"ZeFit" in client.get_device_name():
                                if client.send_sms_v2(sender, message) is not None:
                                    print("[i] SMS sended !")
                            else:
                                if client.send_sms(sender, message) is not None:
                                    print("[i] SMS sended !")


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

            except:
                print("[i] Unknown command.")