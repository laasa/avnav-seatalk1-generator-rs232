# avnav-seatalk1-generator-rs232

![grafik](https://user-images.githubusercontent.com/98450191/153687947-2c0b2547-b184-4cfd-bf48-38300e376872.png)

# General

The plugin generates a seatalk 1 protocol output via RS232 every 10 seconds which sets the depth (DBT) to 6,7 meters and speed (STW) to 10,9 km/h.

It is widely based on the seatalk remote plugin (https://github.com/wellenvogel/avnav-seatalk-remote-plugin).

There exist the way to activate the GPIO plugin in openplotter/signalk.
But especially for beginners like me it's possibly a bit to complicate to get knowledge 
- which software serve the hardware, 
- which one is storing the value and 
- what is the way to get these values in avnav.

It takes a bit of time to understand the powerful ideas of multiplexing between all the software in openplotter family.
To get in touch with avnav plugin programming and python and to have simple and short data ways I tried another way.
Especially the last thing could be interesting: To have the most current 'depth below transducer' value and not the 2 seconds old one.

So the idea behind this plugin is to create other plugins to read seatalk1 protocol frames via rs232(PC) or gpio (RPI) without using signalk way.
With that plugin you can test these plugins without your boat on your side (currently it's winter: to cold to try it out in real).

# Parameter

- device: e.g. '/dev/ttyUSB0'
- usbid: as alternative for devive name

# Details

The Seatalk 1 protocol is simply written to the selected device every 10 seconds.
The following bytes are written to RS232:

DPT 'Depth below transducer' of 6,7 meters
- Byte 1: Command byte             : 0x00 => parity bit is set to mark up the start of Seatalk protocol
- Byte 2: Attribute byte           : 0x02 => LSB is the number of following bytes (n=2)
- Byte 3: First mandatory data byte: 0x00 => YZ: in feets
- Byte 4: optionially data byte 1  : 0xdd: LSB for value for 'Depth below transducer'
- Byte 5: optionially data byte 2  : 0x00: MSB for value for 'Depth below transducer'
The resulting value for 'Depth below transducer' is 0x00dd/10 feets (221/10 feets = 22,1 feets = 6,7 meters).

STW 'Speed Through Water' of 10,9 km/h
- Byte 1: Command byte             : 0x20 => parity bit is set to mark up the start of Seatalk protocol
- Byte 2: Attribute byte           : 0x01 => LSB is the number of following bytes (n=1)
- Byte 3: First mandatory data byte: 0x3B => LSB for value for 'Speed Through Water'
- Byte 4: optionially data byte 1  : 0x00: MSB for value for 'Speed Through Water'
The resulting value for 'Speed Through Water' is 0x003b/10 kn (59/10 kn = 5,9 kn = 10,9 km/h).

# Hardware needs
You need to have a circuit to convert from RS232 level to Seatalk 1 level (described in http://www.thomasknauf.de/rap/seatalk3.htm).

I have used only the TXD part here with an pullup of 10K to +12V.

# Installation

To install this plugin please 
- install packages via: sudo apt-get update && sudo apt-get install python3-serial
- create directory '/usr/lib/avnav/plugins/seatalk1-generator-rs232' and 
- and copy the file plugin.py to this directory.

# Known issues

# Helpers
Setup the serial devices by their serial numbers
- Label your first USB serial device (e.g SeatalkOut)
- Connect the first USB serial device to the PC
- Get the vendorID, deviceID and serial number of the tty device (here "/dev/ttyUSB0")
   udevadm info -a -n /dev/ttyUSB0 | grep {idVendor} | head -n1  => ATTRS{idVendor}=="0403" 
   udevadm info -a -n /dev/ttyUSB0 | grep {bcdDevice} | head -n1 => ATTRS{bcdDevice}=="0600"
   udevadm info -a -n /dev/ttyUSB0 | grep {serial} | head -n1    => ATTRS{serial}=="A10KKBM3"
- creates an udev rule
  mcedit sudo mcedit /etc/udev/rules.d/10-local.rules
   SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A10KKBM3", MODE="0666", SYMLINK+="ttyUSB_SeatalkOut"
- Continue with the next devices
- at the end the file /etc/udev/rules.d/10-local.rules may look like that
    SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A10KKF9V", MODE="0666", SYMLINK+="ttyUSB_SeatalkInp"
    SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A10KKBM3", MODE="0666", SYMLINK+="ttyUSB_SeatalkOut"
- Use this names in avnav (e.g: "/dev/ttyUSB_SeatalkOut")
