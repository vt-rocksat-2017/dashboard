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

class ADSB_Server(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self,name = 'ADSBServer')
        self._stop          = threading.Event()
        self.ip             = options.adsb_ip
        self.port           = options.adsb_port
        self.id             = options.id
        self.ts             = options.ts
        self.sock           = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.connected      = False

        self.log_fh = setup_logger(self.id, 'adsb', self.ts)
        self.logger = logging.getLogger('adsb')

        self.last_frame_ts  = dt.datetime.utcnow()  #Time Stamp of last received frame
        
        self.adsb_count = 0 #number of individual ADSB messages received
        self.q = Queue()

    def run(self):
        print "ADSB Server Running..."
        try:
            print 'trying to connect to VRS'
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print self.utc_ts() + "Connected to Virtual Radar Server..."
        except Exception as e:
            self.Handle_Connection_Exception(e)

        while (not self._stop.isSet()):
            if self.connected == True: 
                if (not self.q.empty()): #new message in Queue for downlink
                    adsb_frame = self.q.get() #should be 256 byte messages
                    msgs = self.Decode_ADSB_Frame(adsb_frame)
                    self.send_to_plotter(msgs)
            elif self.connected == False:
                print self.utc_ts() + "Disconnected from Virtual Radar Server..."
                time.sleep(1)
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    #self.sock.settimeout(1)
                    self.sock.connect((self.ip, self.port))
                    self.connected = True
                    print self.utc_ts() + "Connected to Virtual Radar Server..."
                except Exception as e:
                    self.Handle_Connection_Exception(e)

    def Decode_ADSB_Frame(self, frame):
        msgs = []
        print binascii.hexlify(frame)
        #msg_type   = numpy.uint8(struct.unpack('>B',rx_frame[10]))[0]     #message type, 0=ADSB, 1=AIS, 2=HW
        msg_cnt     = numpy.uint8(struct.unpack('>B',frame[11]))[0]         #Number of ADSB Messages
        length      = numpy.uint32(struct.unpack('<I',frame[12:16]))[0]     #Length indicator field
        data        = frame[16:]
        print msg_cnt, "{0:032b}".format(length), len(data)

        MASK = numpy.uint32(1) #initialize 32 bit number to 31 0s and a 1
        #print "{0:032b}".format(MASK) 
        idx = 0 #first byte in data field index
        for i in range(msg_cnt):
            msg_len = 0 #in bytes
            if (MASK & length) > 0:  #long message
                msg_len = 14
                msg = data[idx:] 
            else:  msg_len = 7
            msg = data[idx:idx+msg_len]
            idx = idx+msg_len
            print i, "{0:032b}".format(MASK), "{0:032b}".format(MASK & length), msg_len, binascii.hexlify(msg)
            msgs.append(msg)
            MASK = MASK << 1 #bit shift MASK for next iteration
        return msgs

    def send_to_plotter(self,msgs):
        for msg in msgs:
            msg_str = '*' + str(binascii.hexlify(msg)) + ';\n'
            #print 'sending', msg_str
            try:
                self.sock.send(msg_str)
            except Exception as e:
                self.Handle_Connection_Exception(e)
            

    def Handle_Connection_Exception(self, e):
        #print e, type(e)
        errorcode = e[0]
        if errorcode==errno.ECONNREFUSED:
            pass
            #print errorcode, "Connection refused"
        elif errorcode==errno.EISCONN:
            print errorcode, "Transport endpoint is already connected"
            self.sock.close()
        else:
            print e
            self.sock.close()
        self.connected = False

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(dt.datetime.utcnow()) + " UTC | "

