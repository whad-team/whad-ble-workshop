---
marp: true
theme: gaia
---

# WHAD BLE workshop

---

<!-- _class: lead -->

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

<!-- _class: lead -->

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
<!-- _class: lead -->

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