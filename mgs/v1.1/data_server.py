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

        self.last_frame_ts  = dt.datetime.utcnow()  #Time Stamp of last received frame

        self.frame_count    = 0
        self.adsb_count     = 0
        self.ais_count      = 0
        self.hw_count       = 0

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
                data = self.sock.recv(4096)
                if len(data) == 256:
                    self.Decode_Frame(data, dt.datetime.utcnow())
                else:
                    self.connected = False
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
            self.adsb_count += 1
            self.adsb_cb.q.put(rx_frame)
        elif msg_type == 1: msg_type_str = ' AIS'
        elif msg_type == 2: msg_type_str = '  HW'
        
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

    def get_frame_counts(self):
        self.valid_count = len(self.valid.time_tx)        
        self.fault_count = len(self.fault.time_tx)
        self.recon_count = len(self.recon.time_tx)
        self.total_count = self.valid_count + self.fault_count + self.recon_count
        #print self.utc_ts(), self.total_count, self.valid_count, self.fault_count, self.recon_count
        return self.total_count, self.valid_count, self.fault_count, self.recon_count

    def set_start_time(self, start):
        print self.utc_ts() + "Mission Clock Started"
        ts = start.strftime('%Y%m%d_%H%M%S')
        self.log_file = "./log/rocksat_"+ self.id + "_" + ts + ".log"
        log_f = open(self.log_file, 'a')
        msg = "Rocksat Receiver ID: " + self.id + "\n"
        msg += "Log Initialization Time Stamp: " + str(start) + " UTC\n\n"
        log_f.write(msg)
        log_f.close()
        self.log_flag = True
        print self.utc_ts() + "Logging Started: " + self.log_file
        self.valid_start = True
        self.start_time = start
        for i in range(len(self.valid.time_rx)):
            self.valid.rx_offset[i] = (self.valid.time_rx[i]-self.start_time).total_seconds()

    def set_adsb_callback(self, callback):
        self.adsb_cb = callback
        #print 'set adsb callback'

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(dt.datetime.utcnow()) + " UTC | "

