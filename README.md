# avnav-seatalk1-generator-rs232
The plugin generates a seatalk 1 protocol output via RS232 every 10 seconds.
The protocol is written to the selected device (e.g. '/dev/ttyUSB0').
The following bytes are written to RS232:
- Command   byte: 0x00: parity bit is set to mark up the start of Seatalk protocol
- Attribute byte: 0x02: 2 following bytes
- Addtional byte: 0x12: LSB for value for 'Depth below transducer'
- Addtional byte: 0x34: MSB for value for 'Depth below transducer'
The resulting value for 'Depth below transducer' is 0x3412/10 feets (13330/10 feets = 1333 feets = 406,2984 meters).
You need to have a circuit to convert to Seatalk 1 level (described in http://www.thomasknauf.de/rap/seatalk3.htm: only the TXD part).
To install this plugin please copy the file plugin.py to '/usr/lib/avnav/plugins/seatalk1-generator'.
