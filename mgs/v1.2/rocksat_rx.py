#!/usr/bin/env python
#########################################
#   Title: Rocksat Telemetry Dashboard  #
# Project: Rocksat-X Competition        #
# Version: 1.1                          #
#    Date: Jul 06, 2016                 #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: This is the initial version  # 
#########################################

import math
import string
import time
import sys
import os
import socket
import threading
import datetime as dt
from optparse import OptionParser
from data_server import *
from adsb_thread import *
from ais_thread import *
from hw_thread import *

def main():
    start_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S.%f")
    #--------START Command Line option parser------------------------------------------------------
    usage  = "usage: %prog "
    parser = OptionParser(usage = usage)
    #Main Parameters
    h_ts    = "Startup Timestamp: [default=%default]"
    h_ip    = "Set Rocksat Receiver Modem IP [default=%default]"
    h_port  = "Set Rocksat Receiver Modem Port [default=%default]"
    h_loc   = "Set Rocksat Receiver ID [default=%default]"
    parser.add_option("-t", "--ts"  , dest="ts"   , type="string", default=start_ts  , help=h_ts)    
    parser.add_option("-a", "--ip"  , dest="ip"   , type="string", default="0.0.0.0" , help=h_ip)
    parser.add_option("-p", "--port", dest="port" , type="int"   , default="52003"   , help=h_port)
    parser.add_option("-i", "--id"  , dest="id"   , type="string", default="VTGS"    , help=h_loc)

    #ADSB Parameters
    h_adsb_ip   = "Set Virtual Radar Server IP [default=%default]"
    h_adsb_port = "Set Virtual Radar Server Port [default=%default]"
    parser.add_option("-b", dest = "adsb_ip"   , action = "store", type = "string", default='127.0.0.1', help = h_adsb_ip)
    parser.add_option("-c", dest = "adsb_port" , action = "store", type = "int"   , default='30003'    , help = h_adsb_port)

    #AIS Parameters
    h_ais_ip   = "Set OpenCPN IP [default=%default]"
    h_ais_port = "Set OpenCPN Port [default=%default]"
    parser.add_option("-d", dest = "ais_ip"   , action = "store", type = "string", default='127.0.0.1', help = h_adsb_ip)
    parser.add_option("-e", dest = "ais_port" , action = "store", type = "int"   , default='2948'     , help = h_adsb_port)
    
    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------    

    os.system('reset')
    lock = threading.Lock()

    adsb_thread = ADSB_Thread(options)
    adsb_thread.daemon = True
    adsb_thread.start() #non blocking

    ais_thread = AIS_Thread(options)
    ais_thread.daemon = True
    ais_thread.start() #non blocking

    hw_thread = HW_Thread(options)
    hw_thread.daemon = True
    hw_thread.start() #blocking

    #server_thread = Data_Server(options, lock)
    server_thread = Data_Server(options)
    server_thread.daemon = True
    server_thread.set_adsb_callback(adsb_thread)
    server_thread.set_ais_callback(ais_thread)
    server_thread.set_hw_callback(hw_thread)
    server_thread.run() #blocking
    #server_thread.start() #Non-blocking



    sys.exit()


if __name__ == '__main__':
    main()

    
