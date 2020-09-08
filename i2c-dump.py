#!/usr/bin/env python
# encoding: utf-8
"""
Adapted from i2c-test.py from Peter Huewe by Jean-Michel Picod 
Modified by Don C. Weber (cutaway) and InGuardians, Inc. 20141015

Brought up to date September 2020 - Adam Laurie

Depends on:
https://github.com/juhasch/pyBusPirateLite

This file is part of pyBusPirate.

pyBusPirate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBusPirate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from pyBusPirateLite.I2C import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("-o", "--output", dest="outfile", metavar="OUTFILE", type=argparse.FileType('wb'),
            required=True,
            help="File name to write data dump. Example: -o /tmp/i2c_dump.bin")
    parser.add_argument("-d", "--serial-port", dest="bp", default="/dev/ttyUSB0",
                        help="The comm device to connect to. Example: -d /dev/ttyUSB0")
    parser.add_argument("-b", "--block-size", dest="bsize", default=256, type=int,
                        help="EEPROM memory block size. See the EEPROM's data sheet.")
    parser.add_argument("-s", "--size", dest="size", type=int, required=True,
                        help="EEPROM memory size. See the EEPROM's data sheet.")
    parser.add_argument("-S", "--i2c-speed", dest="i2c_speed", default="400kHz",
                        help="5kHz, 50kHz, 100kHz, 400kHz")

    args = parser.parse_args(sys.argv[1:])

    #NOTE: Leave USB speed at max because it never really changes when using the BusPirate.
    i2c = I2C(args.bp, 115200)

    # get to known state  - should work in any mode
    print("Entering binmode: ",)
    i2c.enter_bb()
    if i2c.mode == 'bb':
        print("OK.")
    else:
        print("failed.", i2c.mode)
        sys.exit()

    print("Entering raw I2C mode: ",)
    i2c.enter()
    if i2c.mode == 'i2c':
        print ("OK.")
    else:
        print("failed.", i2c.mode)
        sys.exit()
        
    print("Configuring I2C Power & Pullup - ensure Vpu is connected!")
    i2c.configure(power= True, pullup= True)
    i2c.speed= args.i2c_speed
    i2c.timeout(2.5) # need to calculate this from speed!
    
    print("Dumping %d bytes out of the EEPROM." % args.size)

    # Start dumping 
    for block in range(0, args.size, args.bsize):
        print("read block 0x%02x" % (0xa1 +  ((int) (block / args.bsize) << 1)))
        data= i2c.write_then_read(0x01, args.bsize, [0xa1]) # just let chip read out sequentialy
        args.outfile.write(data)
    args.outfile.close()

    print("Reset Bus Pirate to user terminal: ")
    i2c.hw_reset()
