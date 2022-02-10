# avnav-seatalk1-generator-rs232

# General

The plugin generates a seatalk 1 protocol output via RS232 every 10 seconds which sets the depth value to a nearly fixed value of 269,47368 meters.

It is widely based on the seatalk remote plugin (https://github.com/wellenvogel/avnav-seatalk-remote-plugin).

The idea behind is to create a second plugin to read seatalk1 protocol frames via rs232(PC) or gpio (RPI) without using signalk way.
With that plugin you can test the second plugin without a boat (it is winter project: to cold to try it out in real).

# Parameter

- device: e.g. '/dev/ttyUSB0'
- usbid: as alternative for devive name

# Details

The Seatalk 1 protocol is simply written to the selected device every 10 seconds.
The following bytes are written to RS232:
- Byte 1: Command byte             : 0x00 => parity bit is set to mark up the start of Seatalk protocol
- Byte 2: Attribute byte           : 0x02 => LSB is the number of following bytes (n=2)
- Byte 3: First mandatory data byte: 0x00 => YZ: in feets
- Byte 4: optionially data byte 1  : 0x11: LSB for value for 'Depth below transducer'
- Byte 5: optionially data byte 2  : 0x22: MSB for value for 'Depth below transducer'
The resulting value for 'Depth below transducer' is 0x2211/10 feets (8721/10 feets = 872,1 feets = 265,81608 meters).

# Hardware needs
You need to have a circuit to convert from RS232 level to Seatalk 1 level (described in http://www.thomasknauf.de/rap/seatalk3.htm: only the TXD part).
![grafik](https://user-images.githubusercontent.com/98450191/153191823-b1585581-9782-45ab-b2a4-1c544deb7676.png)

# Installation

To install this plugin please 
- create directory '/usr/lib/avnav/plugins/seatalk1-generator' and 
- and copy the file plugin.py to it.

# Known issues
Changing the parity flag doesn't really work here. 
But Could imagine several reasons (USB-to-RS232-dongle, DIY hardware, python serial).
With that given code I got the seatalk protocol '$STALK,00,02,00,89,22' (when reading via GPIO on raspberry). 
Therefore I see 0x2289/10 feets on signalk server (8841/10 feets = 269,47368 meters).
That is not what I expected but it's good enough to do the real job: reading the seatalk protocol inside avnav protocol directly.
