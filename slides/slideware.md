---
marp: true
theme: qb
class:
header: '![height:50px](img/qb.png)'
paginate: true
style: @import url('./css/font-awesome.min.css');

---

<!-- _paginate: skip -->

<style>

img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>

# BLE Hacking 101 with WHAD

##### Romain Cayre, Damien Cauquil 

![width:150 center](img/logo-pts.png)

---

# Who are we ? 

**Romain Cayre**, EURECOM
  - maintainer of *Mirage*, a popular BLE swiss-army tool
  - loves *cross-protocol attacks* (*Wazabee*)

##

**Damien Cauquil**, Quarkslab
  - maintainer of *Btlejack*, another BLE swiss-army tool
  - loves reversing stuff, including *embedded systems*

---

# Agenda

- **What is WHAD ?**
- **Discovering BLE devices**
- **Interacting with a BLE device**
- **Creating fake BLE devices**
- **Breaking BLE legacy pairing**
- **Python scripting**


---

# Workshop goals

- Introduce WHAD, present its features and why it’s cool !
- Demonstrate the basic BLE tools to:
  - handle WHAD interfaces
  - discover BLE devices
  - interact with BLE devices
  - emulate fake BLE devices
- Teach simple Python scripting with WHAD
- Let you experiment with the framework and tools
---

<!-- _class: chapter -->

# What is WHAD ?

---

# A tool for everyone 

![](./img/whad_for_everyone.png)

---

# Global overview

![width:800px](./img/whad-overview.png)

- Harmonised Host / RF Hardware **communication protocol**
- **Python library** supporting multiple wireless protocols
- Multiple user-friendly **CLI tools** that can be combined
- Set of firmwares for **various hardware devices**



---

# Core concepts

![width:600px](img/simple_firmware.png)

Offload complexity as much as possible:
- Protocol stacks implemented on host side
- **Hardware does hardware stuff:** timing-critical tasks, RF

---

# Core concepts

<img src="./img/systematization.png" width="50%">
<ul>
  <li> Generic tools to perform generic tasks/attacks
    <ul style="font-size:0.6em">
      <li>Tools work on multiple protocols</li>
      <li>Some attacks are basically carried out almost the same way no matter the protocol: <br/><strong> → based on primitives infered from our systematization of wireless attacks</strong> </li>
    <li>Common and standardized file format (PCAP) </li>
    <li>Generic tools can be chained to create complex tools (inspired by UNIX philosophy)</li>
  </ul>
  </li>

---

# Compatible hardware

- **Hardware is discoverable** and exposes its *capabilities*

- Generic and custom tools can **tune attacks or tasks** to hardware

- Anyone can develop a compatible firmware <br>**without bothering about tools**

---

# Compatible hardware

![width:1000px](img/compatible_hardware.webp)



---

# Supported protocols
![width:100% center](img/supported_protocols.png)


---

# WHAD protocol

![width:100% center](img/whad_protocol.png)

---

# Connectors and interfaces

![width:550px](img/connectors_and_devices.png)

---

# Tool chaining

![width:900px center](img/whad-toolchain.png)


---

# Python scripting

WHAD provides an user-friendly Python API to implement your own custom scripts:

```python
import sys
from whad.ble import Central
from whad.ble.profile import UUID
from whad.device import WhadDevice

# Create the Central connector & the WHAD device
central = Central(WhadDevice.create("hci0"))
device = central.connect('74:da:ea:91:47:e3', random=False)
if device is not None:
    device.discover()
    device_name = device.get_characteristic(UUID(0x1800), UUID(0x2A00))
    print("[i] Device name: ", device_name.value)
    central.close()
else:
    print("Usage: ", sys.argv[0]+" <interface>")
```

---

## Setup
---

# Hardware requirements

- Computer or VM running a **Linux** operating system
- nRF52 USB Dongle with **ButteRFly** installed
- USB Bluetooth Low Energy **dongle** or **embedded Bluetooth adapter**

![width:500px](img/requirements.png)

---

# Resources

- Online repository with examples and code templates:
[https://github.com/whad-team/whad-workshop](https://github.com/whad-team/whad-workshop)



- Virtual machine image:
[https://drive.google.com/file/d/10wKAWlcy5zyRrwxYV8BikEAq5SCYjIOP/view?usp=sharing](https://drive.google.com/file/d/10wKAWlcy5zyRrwxYV8BikEAq5SCYjIOP/view?usp=sharing)

---

# Instaling WHAD locally

Installing whad-client is as simple as running:

<pre>
    <code>$ mkdir whad-workshop && cd whad-workshop
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install whad
(venv) $ winstall --rules all</code>
</pre>


---

# Flashing ButteRFly firmware

Set the dongle in **programming mode** by pressing the side button *RESET*:
![width:500px](img/dongle_press_reset.svg)

Run the following command:

<pre>
<code> $ winstall --flash butterfly
</code>
</pre>

---

# WHAD interfaces

`wup` / `whadup` is the easiest way to detect compatible interfaces on your system:

- automatically detect compatible interfaces (USB and internal)
- query any interface to determine its capabilities
- show capabilities and explain what the device is capable of

---

# WHAD interfaces

List available interfaces:

```
$ wup
```

Enumerate the capabilities of a specific interface *"uart0"*:
```
$ wup uart0
```

---

# WHAD interfaces

![width:90% center](img/wup.png)

---

<!-- _class: handson -->
# whadup / wup

Use `wup` to list all the available interfaces:

```bash
$ wup
```

Use `wup` to show more information about an interface:

```bash
$ wup hci0
```


---

<!-- _class: chapter -->

## Discovering BLE devices

---

# BLE device advertisements

- Two types of PDU sent by BLE devices:
    - **Advertisement PDUs**: *ADV_IND*, *ADV_DIRECT_IND*, *ADV_NONCONN_IND*, etc...
    - **Scan-related PDUs** (active mode): *SCAN_REQ* and *SCAN_RSP*

- Advertisement and Scan PDUs are sent (at least) on **advertising channels** (**37**, **38**, **39**)

---

# Sniffing advertising PDUs

- `wsniff` provides a dedicated mode when domain is set to **ble**:

```bash
$ wsniff -i uart0 ble -a
```

The `-a` option enables *wsniff*'s BLE advertisement sniffing mode.

**It listens on channel 37 by default**, but you can specify another with the `-c / --channel` option.

**Sniffing is only supported by nRF52840 dongles.**

---

# Scanning for BLE devices

- `wble-central` provides a scanning feature to discover surrounding devices:

```bash
$ wble-central -i hci0 scan
 RSSI Lvl  Type  BD Address        Extra info
[-058 dBm] [PUB] 2c:be:eb:XX:XX:XX 
[-076 dBm] [RND] f2:ea:48:d1:48:c9 name:"ZeFit4 HR#17757"
[-058 dBm] [PUB] a4:c1:38:XX:XX:XX name:"8eyvxxxx"
[-064 dBm] [PUB] d0:d0:03:XX:XX:XX
```

- Unlike sniffing, scanning loops on every advertising channel

---

# Profiling BLE devices

- Some devices expose a **GATT server** with a set of **services** and **characteristics**

- *GATT enumeration procedure* discovers services and characteristics for a specific device but:
    - It may be <u>slow</u> depending on the target device
    - Performed **multiple times** when required by different tools

- WHAD can **save a BLE device's GATT profile into a JSON file**

- This file can then be used to **skip GATT enumeration**

---

# Profiling BLE devices

- `wble-central` provides a specific `profile` command to connect to a specific device and save its *profile* to a JSON file:

```bash
$ wble-central -i hci0 -b f2:ea:48:d1:48:c9 -r profile my_device.json
```

`-r` option is mandatory when dealing with a device that uses a *random* BD address

---

# BLE profile example

```json
{
    "services": [
        {"uuid": "1800", "type_uuid": "2800", "start_handle": 1, "end_handle": 7, "characteristics": [...]},
        {"uuid": "1801", "type_uuid": "2800", "start_handle": 8, "end_handle": 8, "characteristics": []},
        {"uuid": "6006", "type_uuid": "2800", "start_handle": 9, "end_handle": 14, "characteristics": [...]},
        {"uuid": "7006", "type_uuid": "2800", "start_handle": 15, "end_handle": 20, "characteristics": [...]},
        {"uuid": "180D", "type_uuid": "2800", "start_handle": 21, "end_handle": 65535, "characteristics": [...]},
    ],
    "devinfo": {
        "adv_data": "10095...",
        "bd_addr": "f2:ea:48:d1:48:c9",
        "addr_type": 1,
        "scan_rsp": ""
    }
}
```

---

<!-- _class: chapter -->

# Interacting with BLE devices

---

# `wble-central` interactive mode

- Provides a set of commands to:
  - scan for BLE devices
  - connect to a BLE device
  - enumerate its GATT profile
  - interact with its exposed characteristics

- To use it, simply run:

```bash
$ wble-central -i hci0
```

---

# Scanning and connecting to a device

```bash
wble-central> scan
 RSSI Lvl  Type  BD Address        Extra info
[-078 dBm] [RND] f2:ea:48:d1:48:c9 name:"ZeFit4 HR#17757"
```

```bash
wble-central> connect f2:ea:48:d1:48:c9
```

- Successful connection:

```
Successfully connected to target f2:ea:48:d1:48:c9
wble-central|f2:ea:48:d1:48:c9>
```

---

# GATT enumeration

- Once connected, use the `profile` command:

```bash
wble-central|f2:ea:48:d1:48:c9> profile
```

```bash
Service Generic Access (0x1800)

 Device Name (0x2A00) handle: 2, value handle: 3
  | access rights: read, write

...
```

GATT enumeration is **required to use UUIDs** in future operations.

---

# Reading a characteristic's value

- Use the `read` command with the characteristic's UUID:

```bash
wble-central|f2:ea:48:d1:48:c9> read 2a00
```

```bash
00000000: 5A 65 46 69 74 34 20 48  52 23 31 37 37 35 37     ZeFit4 HR#17757
```

- Use the `read` command with the characteristic's value handle (3):

```bash
wble-central|f2:ea:48:d1:48:c9>read 3
```

---

# Writing to a characteristic's value

- Use the `write` command with the characteristic's UUID:

```bash
wble-central|f2:ea:48:d1:48:c9> write 2A00 "Hello"
```

- Use the `write` command with the characteristic's value handle:

```bash
wble-central|f2:ea:48:d1:48:c9> write 3 "Hello"
```

- Write data in hex ("ABCD"):

```bash
wble-central|f2:ea:48:d1:48:c9> write 2A00 hex 41 42 43 44
```

---

# Writing to a characteristic's value

- Try to write into a non-writeable characteristic's value:

```bash
wble-central|f2:ea:48:d1:48:c9> >write 19 "Hello"
[!] ATT error: write operation not allowed
```

- Write without waiting a response with `write-cmd`:

```bash
wble-central|f2:ea:48:d1:48:c9> writecmd 3 "Hacked"
```

---

# Subscribing to notifications

- Use the `sub` command with the characteristic's UUID:

```bash
wble-central|f2:ea:48:d1:48:c9> sub 2a37
```

- or with the characteristic's handle:

```bash
wble-central|f2:ea:48:d1:48:c9> sub 22
```

---

# Real-time monitoring

- Use the `wireshark` command to start a live wireshark monitor:

```bash
wble-central|f2:ea:48:d1:48:c9> wireshark on
```

- Run a `profile` command and let the magic happens

![bg right 90%](img/ble-wireshark-monitor.png)

---

<!-- _class: chapter -->

# Scripting with WHAD, a primer

---

# Scripting with WHAD

- WHAD's interactive shell supports scripting **by default**

- Scripting is useful when:
  - Some devices expect to receive data **in a short time window**
  - you want to **automate** one or more tasks/attacks

- Scripts are **simple text files** with *.whad* extension
  - commands are executed one after the other
  - basic scripting language

--- 

# Manipulating the environment

- WHAD interactive shells use a dedicated *environment* to create, store and recall **variables**

- To create a variable: `set NAME VALUE`

```bash
set TARGET "f2:ea:48:d1:48:c9"
```

- To use a variable: `$VAR_NAME`

```sh
connect $TARGET
```

---

# Manipulating the environment

- To delete a variable: `unset VAR_NAME`

```bash
unset TARGET
```

- To list current environment: `env`

```bash
wble-central> env
TOTO=tralala
TARGET=f2:ea:48:d1:48:c9
```

---

# Some useful scripting commands

- To print some text or value: `echo TEXT`

```bash
echo "Connecting to " $TARGET
```

- Wait for the user to press a key: `wait MESSAGE`

```bash
wait "Press a key to disconnect from target"
```

---

# Scripting with `wble-central`

- Quick whad script to connect to a target (*example.whad*):

```sh
set TARGET "f2:ea:48:d1:48:c9"
echo "Connecting to " $TARGET "..."
connect $TARGET random
```

- Run script with `wble-central`, using the `-f` option:

```bash
$ wble-central -i hci0 -f ./example.whad
```

---

# Hands-on

- Write a script that connects to your watch and:
  - discovers its services and characteristics
  - read the *DeviceName* characteristic from its *Generic Access* service and prints it
  - writes "0wn3d" into the same *DeviceName* characteristic value
  - disconnects properly from the device

---

# Hands-on

1. Export your watch GATT profile into a JSON file using `wble-central`

2. Modify the previous script to load this JSON file using the interactive shell's `profile` command

3. Verify that this new script runs much faster


---

<!-- _class: chapter -->
# Creating fake BLE devices

---

# `wble-periph` interactive mode

- Provides a **set of commands** to:
  - configure the device's advertising data
  - create GATT services and characteristics
  - modify characteristics's properties and values
  - start and stop advertising

- **Displays every client GATT operation** in real-time

- Allows user to **modify characteristics's values** even when a GATT client is connected !

---

# Creating a fake peripheral by hand

- Start `wble-periph` in interactive mode:

```bash
$ wble-periph -i hci0
```

- Use the `name` command to set the device name:

```bash
wble-periph> name "EmulatedDevice"
```

- Add a *Generic Access* service using the `service` command:

```bash
wble-periph> service add 1800
```

---

# Creating an emulated peripheral by hand

- Create a *Device Name* characteristic using the `char` command:

```bash
wble-periph|service(1800)> char add 2a00 read write notify
```

This characteristic is declared as <u>readable</u>, <u>writeable</u> and supports <u>notifications</u>.

- Set the characteristic value with `write`:

```bash
wble-periph|service(1800)> write 2a00 "EmulatedDevice"
```

---

# Check the device's GATT profile

- Use the `back` command to exit GATT service edition mode

```bash
wble-periph|service(1800)> back
```

- Use the `service` command to print the current GATT profile:

```
wble-periph> service

Service 1800 (Generic Access) (handles from 1 to 4):
└─ Characteristic 2a00 (Device Name)
  └─ handle:2, value handle: 3, props: read,write,notify
  └─ Descriptor 2902 (handle: 4)
```

---

# Start advertising

- Use the `start` command to tell `wble-periph` to start advertising:

```
wble-periph> start
```

When the emulated device is advertising, no more changes can be made to the GATT profile configured previously.

---

# Connect to your emulated device

- Using *nRF Connect*, connect to your emulated device and read its *Device Name* characteristic

- `wble-periph` should display something like:

```
wble-periph> start
New connection handle:24
Reading characteristic 2a00 of service 1800
 00000000: 46 61 6B 65 44 65 76 69  63 65                    FakeDevice
```

---

# Notifications

- Subscribe to notifications for the *Device Name* characteristic

- Use the `write` command to update the characteristic's value:

```
wble-periph[running]> write 2a00 "EmulatedDevice!"
```

- Notice the value has changed in *nRF Connect*

---

# Monitoring with Wireshark

- Use the `wireshark` command to spawn Wireshark and monitor live GATT operations:

```
wble-periph[running]> wireshark on
```

---

# Device cloning

Use a saved GATT profile (JSON) with `wble-periph`:

<pre><code>$ wble-periph -i hci0 -p profile.json</code></pre>

It will automatically copy the emulated device profile including:
- its services, characteristics, descriptors and values
- its advertising data and scan response (if used)

---

<!-- _class: chapter -->
# Scripting `wble-periph`

---

# Automate peripheral creation

`emulated.whad`

<pre><code>name "MyEmulatedDevice"
echo "Configuring services and characteristics ..."
service 18a00
char add 2a00 read write notify
write 2a00 "MyEmulatedDevice"
back
echo "Starting emulated device ..."
start
wait "Press any key to exit."</code></pre>

To run this script:

<pre><code>$ wble-periph -i hci0 -f emulated.whad</code></pre>

---

<!-- _class: chapter -->
# Breaking BLE legacy pairing

---

# BLE pairing vs bonding

- Bluetooth Low Energy **pairing** allows to negotiate security keys (e.g., encryption) to encrypt and authenticate the link

- Bluetooth Low Energy **bonding** is a variant of BLE pairing where the devices will store the distributed keys for later use

---

# BLE pairing overview

<img src="img/pairing.png" width="65%" style="margin-top:50px;" />


---

# Legacy pairing - passkey entry

<img src="img/legacy_pairing.png" width="60%" style="margin-top:60px;" />


---

# CrackLE

- Legacy Pairing is known to be vulnerable to a key recovery attack: **crackLE**, that allows an attacker to guess or very quickly brute force the TK (Temporary Key). 
- With the TK and other data collected from the pairing process, the STK (Short Term Key) and later the LTK (Long Term Key) can be collected.
- With the STK and LTK, all communications between the Central and the Peripheral can be decrypted.

---

# CrackLE attack with WHAD


<img src="img/crackle.png" />
<ul>
<li> Sniffing the pairing process and the encrypted traffic:
</li>

```
$ wsniff -i uart0 ble -f | wdump pairing.pcap
```
<li> Recovering the Short Term Key (STK):
</li>

```
$ wplay pairing.pcap | wanalyze legacy_pairing_cracking
[✓] legacy_pairing_cracking → completed
  - tk:  00000000000000000000000000000000
  - stk:  11223344112233441122334411223344
```

---

# CrackLE attack with WHAD


<ul>

<li> Recovering the distributed keys (LTK, IRK, CSRK):
</li>

```
$ wplay --flush pairing.pcap -d -k 11223344112233441122334411223344 | wanalyze
[...]
[✓] ltk_distribution → completed
  - ltk:  2867a99de17e3548cc17cf16ef96050e
  - rand:  38a7dcd10a1a93c6
  - ediv:  29507

[✓] irk_distribution → completed
  - address:  74:da:ea:91:47:e3
  - irk:  13c3a68f113b764cc8e73f55fc52c002

[✓] csrk_distribution → completed
  - csrk:  c3062f93c91eef96354edcd70a1a0306
[...]
```

---

# wanalyze

<img src="img/handson.png" style="height:80%; position:absolute;top:100px; left:50px;" />
<div style="width:80%;position:absolute; top:100px; left:200px;">
Use <code>wplay</code> and <code>wanalyze</code> to recover the Long Term Keys distributed in the following PCAP:   
<br /><br />
<a style="font-size:0.5em" href="https://github.com/whad-team/whad-client/raw/refs/heads/main/whad/resources/pcaps/ble_pairing.pcap"> https://github.com/whad-team/whad-client/raw/refs/heads/main/whad/resources/pcaps/ble_pairing.pcap</a>
</div>


---

## Python scripting

---

# Python API 101

- WHAD provides an user-friendly Python API if you want to write your custom scripts

- Very convenient way to automate things or implement complex behaviours !


---
# Devices & connectors

- Start by initating the communication with your RF hardware:

```python
from whad.device import WhadDevice
dev = WhadDevice.create("uart0")
```

- Then, you can use a dedicated **connector** (Scanner, Central, Peripheral, Sniffer...) that will expose you a specialized API:
```python
from whad.ble import Scanner
scanner = Scanner(dev)
```

```python
from whad.ble import Central
central = Central(dev)
```

---
# Closing a connector
- You can properly close a connector using the `close` method:
```python
from whad.device import WhadDevice
from whad.ble import Central

try:
  dev = WhadDevice.create("uart0")
  central = Central(dev)
  while True:
    pass
except KeyboardInterrupt:
  central.close()
  ```

---
# Discovering BLE devices
- To discover surrounding BLE devices, instantiate a `Scanner` connector and use the `discover_devices` method:

```python
from whad.device import WhadDevice
from whad.ble import Scanner

scanner = Scanner(WhadDevice.create("hci0"))
for device in scanner.discover_devices():
  print(device.address, "->", device.name)

```
---
# Connecting to a device
- Connecting to a BLE device is as simple as instantiating a `Central` connector:

```python
from whad.device import WhadDevice
from whad.ble import Central

central = Central(WhadDevice.create("hci0"))
```
 - and use the `connect` method:
 ```python
 target = central.connect('11:22:33:44:55:66')
 ```
 ```python
 target = central.connect('AA:BB:CC:DD:EE:FF', random=True)
 ```

---
# Discovering a GATT profile

- Once connected, you can discover services and characteristics using the `discover` method:
```python
  from whad.device import WhadDevice
  from whad.ble import Central

  central = Central(WhadDevice.create("hci0"))
  target = central.connect('11:22:33:44:55:66')

  # Discover and display the profile
  target.discover()
  print("[i] Discovered profile")
  for service in target.services():
      print('-- Service %s' % service.uuid)
      for charac in target.characteristics():
          print(' + Characteristic %s' % charac.uuid)
```
---
# Find characteristic by UUID

- You can easily access a specific characteristic from its UUID:
```python
from whad.ble.profile import UUID

# [...] 

# Retrieve the DeviceName characteristic object
device_name = target.get_characteristic(UUID(0x1800), UUID(0x2A00))
print(device_name.name)
```

---
# Reading a characteristic value

- Once you got your characteristic object, you can read the characteristic value using:
```python
# Reading the remote device name
device_name = target.find_characteristic_by_uuid(UUID(0x2A00))
print(device_name.value)
```
- It will trigger a *read request* for the corresponding characteristic (or several if values are longer than the MTU), even if you have no read access !


---
# Writing into a characteristic value

- Writing to a characteristic’s value is quite as simple as reading it, we just set the characteristic’s value attribute and it starts a GATT write operation:
```python
# Writing the remote device name
device_name = target.find_characteristic_by_uuid(UUID(0x2A00))
device_name.value = b"pwnd"
```

- By default, it will trigger a *write request*. If you want to use *write command* (no response), use:
```python
# Writing the remote device name through a write command operation
device_name = target.find_characteristic_by_uuid(UUID(0x2A00))
device_name.write(b"pwnd", without_response=True)
```

---
# Subscribing for notifications


- To subscribe for notification, start by writing a callback:
```python
def notification_callback(charac, value: bytes, indication=False):
  print(f"Characteristic {charac.name} value has been changed to {value.hex()}")
```

- Then, subscribe for notification using:

```python
device_name = target.find_characteristic_by_uuid(UUID(0x2A00))
if device_name.can_notify():
    if device_name.subscribe(
        notification = True,
        callback = notification_callback
    ):
      print("[i] Successfully susbcribed !")
    else:
      print("[i] An error occured.")
```

---
# Subscribing for indication

- To subscribe for indication, callback is very similar:
```python
def indication_callback(charac, value: bytes, indication=False):
  # indication parameter equals True
  print(f"Characteristic {charac.name} value has been changed to {value.hex()}")
```

- Then, subscribe for indication:

```python
device_name = target.find_characteristic_by_uuid(UUID(0x2A00))
if device_name.can_indicate():
    if device_name.subscribe(
        indication=True,
        callback = indication_callback
    ):
      print("[i] Successfully susbcribed !")
    else:
      print("[i] An error occured.")
```

---
# Unsubscribing
- Both for indication and notification, you can unsubscribe at any time using:
```python
# Unsubscribe from notifications or indications
if device_name.unsubscribe():
    print(f"Successfully unsubscribe from characteristic {device_name.uuid}")
```
---
# Synchronous mode

- Sometimes it may be convenient to disable the stack temporarily and handle the PDUs processing by yourself. It can be done by enabling the synchronous mode:
```python
    # Enable synchronous mode: we must process any incoming BLE packet.
    central.enable_synchronous(True)
```


- Then, all the PDUs will not be forwarded to the stack but appended to a queue instead.

---
# Sending handcrafted PDUs

- It's then possible to inject your own handcrafted PDUs:
```python
central.send_pdu(BTLE_DATA()/BTLE_CTRL()/LL_VERSION_IND(
    version = 0x08,
    company = 0x0101,
    subversion = 0x0001
))
```
- Then, wait for an answer using something like this:
```python
while central.is_connected():
    pdu = central.wait_packet()
    if pdu.haslayer(LL_VERSION_IND):
        pdu[LL_VERSION_IND].show()
        break
```

---
# Monitoring in and out traffic

- You can attach a callback to monitor all the incoming and outgoing traffic while using a connector:
```python
def processing_callback(pdu):
  pdu.show()

central.attach_callback(processing_callback)
```

---
# Using PCAP monitor

- You can also easily export the traffic into a PCAP file using the PCAP monitor:
```python
from whad.common.monitors import PCAPMonitor

pcap_monitor = PCAPMonitor("out.pcap")

# Attach & start the monitor
pcap_monitor.attach(central)
pcap_monitor.start()

# [...]
# Stop the monitor
pcap_monitor.stop()
```

---
# Using Wireshark monitor

- Similarly, you can watch the live traffic through wireshark using another monitor:
```python
from whad.common.monitors import WiresharkMonitor

ws_monitor = WiresharkMonitor()

# Attach & start the monitor
ws_monitor.attach(central)
ws_monitor.start()

# [...]
# Stop the monitor
ws_monitor.stop()
```

---

## Q/A time


---


## Thank you !
