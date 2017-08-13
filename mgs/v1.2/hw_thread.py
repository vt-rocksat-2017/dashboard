#!/usr/bin/env python
#########################################
#   Title: Rocksat Data Server Class    #
# Project: Rocksat                      #
# Version: 1.0                          #
#    Date: August, 2017                 #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: Initial Version              # 
#########################################

import socket
import threading
import sys
import os
import errno
import time
import binascii
import numpy
from Queue import Queue
import datetime as dt
from logger import *

class HW_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self,name = 'HWThread')
        self._stop          = threading.Event()
        self.ip             = options.ais_ip
        self.port           = options.ais_port
        self.id             = options.id
        self.ts             = options.ts
        self.connected      = False
        self.log_fh = setup_logger(self.id, 'hw_msg', self.ts)
        self.logger = logging.getLogger('hw_msg')

        self.last_frame_ts  = dt.datetime.utcnow()  #Time Stamp of last received frame
        
        self.hw_count = 0 #number of individual ADSB messages received
        self.msgs = None
        self.q = Queue()

    def run(self):
        print "HW Thread Running..."
        while (not self._stop.isSet()):
            if (not self.q.empty()): #new message in Queue for downlink
                hw_frame = self.q.get() #should be 256 byte messages
                self.msgs = self.Decode_HW_Frame(hw_frame)
            

    def Decode_HW_Frame(self,frame):
        self.hw_count += 1
        data = frame[11:]
        self.logger.info(str(self.hw_count)+','+data)
 

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(dt.datetime.utcnow()) + " UTC | "

