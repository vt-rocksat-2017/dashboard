#!/usr/bin/env python
##################################################
# Title: E310 Serial to Ethernet Test
# Author: Zachary James Leffke
# Description: 
#   Test pyserial module on E310
# Generated: April 5, 2016
##################################################

import os
import sys
import time
import string
import serial
import socket
import threading
import random
import numpy
import struct
import ctypes
import binascii

from optparse import OptionParser
from datetime import datetime as date

CALLSIGN = "KJ4WRQ"
    
if __name__ == '__main__':
    #ts = (date.datetime.utcnow()).strftime("%Y%m%d")

    #--------START Command Line option parser------------------------------------------------------
    usage = "usage: %prog <options>"
    parser = OptionParser(usage = usage)

    #----Serial/socket options----
    a_help = "Destination IP Address, [default=%default]"
    p_help = "Destination Port, [default=%default]"
    r_help = "Socket Write Speed [sec], [default=%default]"
    f_help = "source data file, [default=%default]"
    rand_help = "Enable random sleep, [default=%default]"

    parser.add_option("-a","--addr"  ,dest="addr"  ,action="store",type="string",default="0.0.0.0",help=a_help)
    parser.add_option("-p","--port"  ,dest="port"  ,action="store",type="int",default="52001",help=p_help)
    parser.add_option("-r","--rate"  ,dest="rate"  ,action="store",type="float" ,default="0.044",help=r_help)
    parser.add_option("","--rand"  ,dest="rand"  ,action="store",type="int",default="0",help=rand_help)

    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.settimeout(1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.sendto(data, (options.addr, options.port))
    sock.bind((options.addr, options.port))
    count = int(0)
    buff=ctypes.create_string_buffer(2)
    while 1:
        try:
            rx_data, addr = sock.recvfrom(4096) # block until data received on control port
            print count
            print binascii.hexlify(rx_data)
            print rx_data
            print len(rx_data)
            print addr
            count += 1
        except socket.timeout, e:
            print e
        
    
    sys.exit()
