# avnav-seatalk1-generator-rs232

The plugin generates a seatalk 1 protocol output via RS232 every 10 seconds which is set the depth value.

The idea behind is to create a second plugin to read seatalk1 protocol frames via rs232(PC) or gpio (RPI) without using signalk way.
With that plugin you can test the second plugin without a boat (it is winter project: to cold to try it out in real).
It is widely based on the seatalk remote plugin (https://github.com/wellenvogel/avnav-seatalk-remote-plugin).

#Parameter
- device: e.g. '/dev/ttyUSB0'
- usbid: as alternative for devive name

#Details
The Seatalk 1 protocol is simply written to the selected device every 10 seconds.
The following bytes are written to RS232:
- Command   byte: 0x00: parity bit is set to mark up the start of Seatalk protocol
- Attribute byte: 0x02: 2 following bytes without parity bit set
- Addtional byte: 0x12: LSB for value for 'Depth below transducer'
- Addtional byte: 0x34: MSB for value for 'Depth below transducer'
The resulting value for 'Depth below transducer' is 0x3412/10 feets (13330/10 feets = 1333 feets = 406,2984 meters).
You need to have a circuit to convert to Seatalk 1 level (described in http://www.thomasknauf.de/rap/seatalk3.htm: only the TXD part).
![grafik](https://user-images.githubusercontent.com/98450191/153191823-b1585581-9782-45ab-b2a4-1c544deb7676.png)

#Installation
To install this plugin please 
- create directory '/usr/lib/avnav/plugins/seatalk1-generator' and 
- and copy the file plugin.py to it.
