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

import datetime as dt
from logger import *

class Data_Server(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self,name = 'DataServer')
        self._stop          = threading.Event()
        self.ip             = options.ip
        self.port           = options.port
        self.id             = options.id
        self.ts             = options.ts
        self.sock           = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connected      = False

        self.log_fh = setup_logger(self.id, 'main', self.ts)
        self.logger = logging.getLogger('main')

        self.adsb_log_fh = setup_logger(self.id, 'adsb_frame', self.ts)
        self.adsb_logger = logging.getLogger('adsb_frame')

        self.ais_log_fh = setup_logger(self.id, 'ais_frame', self.ts)
        self.ais_logger = logging.getLogger('ais_frame')

        self.hw_log_fh = setup_logger(self.id, 'hw_frame', self.ts)
        self.hw_logger = logging.getLogger('hw_frame')

        self.last_frame_ts  = dt.datetime.utcnow()  #Time Stamp of last received frame

        self.frame_count        = 0
        self.adsb_frame_count   = 0
        self.ais_frame_count    = 0
        self.hw_frame_count     = 0

    def run(self):
        print "Data Server Running..."
        try:
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print self.utc_ts() + "Connected to Modem..."
        except Exception as e:
            self.Handle_Connection_Exception(e)

        while (not self._stop.isSet()):
            if self.connected == True: 
                try:
                    data = self.sock.recv(4096)
                    if len(data) == 256:
                        self.Decode_Frame(data, dt.datetime.utcnow())
                    else:
                        self.connected = False
                except Exception as e:
                    self.Handle_Connection_Exception(e)
            elif self.connected == False:
                print self.utc_ts() + "Disconnected from modem..."
                time.sleep(1)
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.sock.connect((self.ip, self.port))
                    self.connected = True
                    print self.utc_ts() + "Connected to Modem..."
                except Exception as e:
                    self.Handle_Connection_Exception(e)
        sys.exit()

    def Decode_Frame(self, rx_frame, ts):
        self.frame_count += 1
        self.last_frame_ts = ts
        #print str(self.frame_count) + ',' + binascii.hexlify(rx_frame)
        self.logger.info(str(self.frame_count) + ',' + binascii.hexlify(rx_frame))
        self.Decode_Header(rx_frame)

    def Decode_Header(self, rx_frame):
        callsign    = str(rx_frame[0:6])     #Callsign
        dn_pkt_id   = numpy.uint16(struct.unpack('>H',rx_frame[6:8]))[0]     #downlink frame id
        up_pkt_id   = numpy.uint16(struct.unpack('>H',rx_frame[8:10]))[0]    #uplink frame id
        msg_type    = numpy.uint8(struct.unpack('>B',rx_frame[10]))[0]     #message type, 0=ADSB, 1=AIS, 2=HW

        msg_type_str = ""
        if msg_type == 0: 
            msg_type_str = 'ADSB'
            self.adsb_frame_count += 1
            self.adsb_cb.q.put(rx_frame)
            self.adsb_logger.info(str(self.adsb_frame_count) + ',' + binascii.hexlify(rx_frame))
        elif msg_type == 1: 
            msg_type_str = ' AIS'
            self.ais_frame_count += 1
            #print rx_frame
            self.ais_cb.q.put(rx_frame)
            self.ais_logger.info(str(self.ais_frame_count) + ',' + binascii.hexlify(rx_frame))
        elif msg_type == 2: 
            msg_type_str = '  HW'
            self.hw_frame_count += 1
            self.hw_cb.q.put(rx_frame)
            self.hw_logger.info(str(self.hw_frame_count) + ',' + binascii.hexlify(rx_frame))
        
        print self.last_frame_ts, self.frame_count, callsign, dn_pkt_id, up_pkt_id, msg_type_str

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

    def set_adsb_callback(self, callback):
        self.adsb_cb = callback
        #print 'set adsb callback'

    def set_ais_callback(self, callback):
        self.ais_cb = callback
        #print 'set adsb callback'
    
    def set_hw_callback(self, callback):
        self.hw_cb = callback
        #print 'set adsb callback'

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(dt.datetime.utcnow()) + " UTC | "

