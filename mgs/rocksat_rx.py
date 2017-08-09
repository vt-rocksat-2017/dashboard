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

def main():
    start_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S.%f")
    #--------START Command Line option parser------------------------------------------------------
    usage  = "usage: %prog "
    parser = OptionParser(usage = usage)
    h_ts    = "Startup Timestamp: [default=%default]"
    h_ip    = "Set Rocksat Receiver Modem IP [default=%default]"
    h_port  = "Set Rocksat Receiver Modem Port [default=%default]"
    h_loc   = "Set Rocksat Receiver ID [default=%default]"
    parser.add_option("-t", "--ts"  , dest="ts"   , type="string", default=start_ts  , help=h_ts)    
    parser.add_option("-a", "--ip"  , dest="ip"   , type="string", default="0.0.0.0" , help=h_ip)
    parser.add_option("-p", "--port", dest="port" , type="int"   , default="52003"   , help=h_port)
    parser.add_option("-i", "--id"  , dest="id"   , type="string", default="VTGS"    , help=h_loc)
    
    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------    

    os.system('reset')
    lock = threading.Lock()

    #server_thread = Data_Server(options, lock)
    server_thread = Data_Server(options)
    server_thread.daemon = True
    server_thread.run() #blocking
    #server_thread.start() #Non-blocking
    sys.exit()


if __name__ == '__main__':
    main()

    
