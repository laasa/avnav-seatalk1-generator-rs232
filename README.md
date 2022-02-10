# avnav-seatalk1-generator-rs232

# General

The plugin generates a seatalk 1 protocol output via RS232 every 10 seconds which sets the depth value to a nearly fixed value of 269,47368 meters.

It is widely based on the seatalk remote plugin (https://github.com/wellenvogel/avnav-seatalk-remote-plugin).

There exist the way to activate the GPIO plugin in openplotter/signalk.
But especially for beginners like me it's possibly a bit to complicate to get knowledge 
- which software serve the hardware, 
- which one is storing the value and 
- what is the way to get these values in avnav.
It takes a bit of time to understand the powerful ideas of multiplexing between all the software in openplotter family.
To get in touch with avnav plugin programming and python and to have simple and short data ways.
Especially the last thing could be interesting: To have the most current 'depth below transducer' value and not the 2 seconds old one.

So the idea behind this plugin is to create other plugins to read seatalk1 protocol frames via rs232(PC) or gpio (RPI) without using signalk way.
With that plugin you can test these plugins without your boat on your side (currently it's winter: to cold to try it out in real).

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
You need to have a circuit to convert from RS232 level to Seatalk 1 level (described in http://www.thomasknauf.de/rap/seatalk3.htm).

I have used only the TXD part here:

![grafik](https://user-images.githubusercontent.com/98450191/153364093-61c8a10d-0b68-42a2-8dae-0e706e0a035f.png)


# Installation

To install this plugin please 
- create directory '/usr/lib/avnav/plugins/seatalk1-generator-rs232' and 
- and copy the file plugin.py to this directory.

# Known issues
Changing the parity flag is one way for implementing SEATALK via RS232 but doesn't work as expected here. 
I could imagine several reasons like USB-to-RS232-dongle, DIY hardware or inside python serial.
With the implemented code I got the seatalk protocol '$STALK,00,02,00,89,22' mostly of the time (when reading via GPIO on raspberry). 
Therefore I see 0x2289/10 feets on signalk server (8841/10 feets = 269,47368 meters).
That is not what I expected but it's good enough to do the real job: reading the seatalk protocol inside avnav plugin directly.
