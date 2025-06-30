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

<img src="./img/whad_for_everyone.png" width="90%" style="margin-top:150px">

---

# Global overview

<h4> WHAD includes:</h4> 
<ul style="font-size:0.8em">
  <li> An harmonised Host / RF Hardware communication protocol</li>
  <li> A python library handling multiple wireless protocols</li>
    <li> Multiple user-friendly CLI tools that can be chained together</li>
  <li> A set of firmwares for various hardware devices</li>

</ul>

<img src="./img/whad-overview.png" width="90%">


---

# Core concepts
<img src="./img/simple_firmware.png" width="70%">

<ul>
  <li> Offload complexity as much as possible
    <ul style="font-size:0.6em">
      <li>Protocol stacks implemented on host side</li>
      <li><strong>Hardware does hardware stuff:</strong> timing-critical tasks, RF</li>
    </ul>
  </li>
</ul>

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

# Core concepts

<img src="./img/compatible_hardware.webp" width="90%">

<ul>
  <li> Compatible hardware
        <ul style="font-size:0.6em">
      <li>Hardware is discoverable and exposes its capabilities </li>
      <li>Generic and custom tools can tune attacks/tasks to hardware </li>
      <li>Anyone can develop a compatible firmware <strong>without bothering about tools</strong> </li>
    </ul>
  </li>
</ul>

---

# Supported protocols
![width:100% center](img/supported_protocols.png)


---

# WHAD protocol

![width:100% center](img/whad_protocol.png)

---

# Connectors and interfaces

![width:100% center](img/connectors_and_devices.png)

---

# Tool chaining

![width:90% center](img/whad-toolchain.png)


---

# Python scripting

<ul style="font-size:0.8em"><li>WHAD provides an user-friendly Python API to implement your own custom scripts</li></ul>
<img src="img/scripting.png" />

---

## Setup
---

# Hardware requirements

<ul style="font-size:0.8em">
<li> Computer or VM running a <strong>Linux</strong> operating system</li>
<li> nRF52 USB Dongle with <strong>ButteRFly</strong> installed</li>
<li> USB Bluetooth Low Energy <strong>dongle</strong> or <strong>embedded Bluetooth adapter</strong></li>
</ul>
<img src="img/requirements.png" />

---

# Resources

- Online repository with examples and code templates:
[https://github.com/whad-team/whad-workshop](https://github.com/whad-team/whad-workshop)



- Virtual machine image:
[https://drive.google.com/file/d/10wKAWlcy5zyRrwxYV8BikEAq5SCYjIOP/view?usp=sharing](https://drive.google.com/file/d/10wKAWlcy5zyRrwxYV8BikEAq5SCYjIOP/view?usp=sharing)

---

# Instaling WHAD locally

- Installing whad-client is as simple as running:
```
$ mkdir whad-workshop && cd whad-workshop
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install whad
(venv) $ winstall --rules all
```
---

# Flashing ButteRFly firmware
<br />
<ul style="font-size:0.8em">
<li>
Set the dongle in <b>programming mode</b> by pressing the side button <i>RESET</i>:
<img src="img/dongle_press_reset.svg" style="transform:scale(0.7)"/>
</li>
<li> Run the following command:
<pre>
<code> $ winstall --flash butterfly
</code>
</pre>

</ul>

---

# WHAD interfaces

<ul style="font-size:1em">
<li> <code>wup</code> / <code>whadup</code> is the easiest way to detect compatible interfaces on your system !
  
<ul style="font-size:0.8em">
<li>Automatically detect compatible interfaces (USB and internal)</li>
<li>Query any interface to determine its capabilities</li>
<li>Show capabilities and explain what the device is capable of</li></ul>
</ul>

- List available interfaces:
```
$ wup
```
- Display the capabilities of a specific interface *"uart0"*:
```
$ wup uart0
```
---

# WHAD interfaces

![width:90% center](img/wup.png)

---

# whadup / wup

<img src="img/handson.png" style="height:85%; position:absolute;top:50px; left:50px;" />

---

## Q/A time


---


## Thank you !
