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

class AIS_Thread(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self,name = 'AISThread')
        self._stop          = threading.Event()
        self.ip             = options.ais_ip
        self.port           = options.ais_port
        self.id             = options.id
        self.ts             = options.ts
        self.sock           = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.connected      = False
        self.log_fh = setup_logger(self.id, 'ais_msg', self.ts)
        self.logger = logging.getLogger('ais_msg')

        self.last_frame_ts  = dt.datetime.utcnow()  #Time Stamp of last received frame
        
        self.ais_count = 0 #number of individual ADSB messages received
        self.msgs = None
        self.q = Queue()

    def run(self):
        print "AIS Thread Running..."
        try:
            print 'trying to connect to OpenCPN'
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print self.utc_ts() + "Connected to OpenCPN..."
        except Exception as e:
            self.Handle_Connection_Exception(e)

        while (not self._stop.isSet()):
            if (not self.q.empty()): #new message in Queue for downlink
                ais_frame = self.q.get() #should be 256 byte messages
                self.msgs = self.Decode_AIS_Frame(ais_frame)
            if self.connected == True: 
                pass
                self.send_to_plotter(self.msgs)
            elif self.connected == False:
                print self.utc_ts() + "Disconnected from OpenCPN..."
                time.sleep(1)
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    #self.sock.settimeout(1)
                    self.sock.connect((self.ip, self.port))
                    self.connected = True
                    print self.utc_ts() + "Connected to OpenCPN..."
                except Exception as e:
                    self.Handle_Connection_Exception(e)

    def Decode_AIS_Frame(self,frame):
        data = frame[11:]
        #print data
        data_lines = data.split('!')
        #print data_lines
        msgs = []
        for dl in data_lines:
            if len(dl) > 0:
                msgs.append("!" + dl)

        print msgs
        for msg in msgs:
            self.ais_count +=1
            self.logger.info(str(self.ais_count)+','+msg)
        return msgs

    def send_to_plotter(self,msgs):
        if msgs != None:
            for msg in msgs:
                print msg
                msg_str = msg
                #print 'sending', msg_str
                try:
                    self.sock.send(msg_str)
                except Exception as e:
                    self.Handle_Connection_Exception(e)

    def Decode_ADSB_Frame(self, frame):
        msgs = []
        #print binascii.hexlify(frame)
        #msg_type   = numpy.uint8(struct.unpack('>B',rx_frame[10]))[0]     #message type, 0=ADSB, 1=AIS, 2=HW
        msg_cnt     = numpy.uint8(struct.unpack('>B',frame[11]))[0]         #Number of ADSB Messages
        length      = numpy.uint32(struct.unpack('<I',frame[12:16]))[0]     #Length indicator field
        data        = frame[16:]
        #print msg_cnt, "{0:032b}".format(length), len(data)

        MASK = numpy.uint32(1) #initialize 32 bit number to 31 0s and a 1
        #print "{0:032b}".format(MASK) 
        idx = 0 #first byte in data field index
        for i in range(msg_cnt):
            self.adsb_count += 1
            msg_len = 0 #in bytes
            if (MASK & length) > 0:  #long message
                msg_len = 14
                msg = data[idx:] 
            else:  msg_len = 7
            msg = data[idx:idx+msg_len]
            idx = idx+msg_len
            #print i, "{0:032b}".format(MASK), "{0:032b}".format(MASK & length), msg_len, binascii.hexlify(msg)
            msgs.append(msg)
            self.logger.info(str(self.adsb_count)+','+binascii.hexlify(msg))
            MASK = MASK << 1 #bit shift MASK for next iteration
        return msgs

    def send_to_plotter_old(self,msgs):
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

