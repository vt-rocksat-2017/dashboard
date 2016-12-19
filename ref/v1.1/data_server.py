#!/usr/bin/env python
#########################################
#   Title: Rocksat Data Server Class    #
# Project: Rocksat                      #
# Version: 1.0                          #
#    Date: July 06, 2016                #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: Initial Version              # 
#########################################

import socket
import threading
import sys
import os
import errno
import time

from datetime import datetime as date
from utilities import *

class Data_Server(threading.Thread):
    def __init__ (self, options):
        threading.Thread.__init__(self)
        self._stop          = threading.Event()
        self.ip             = options.ip
        self.port           = options.port
        self.id             = options.id #0=VTGS, 1=portable
        self.suspend        = False
        self.sock           = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
        self.connected      = False

        self.valid_count    = 0
        self.fault_count    = 0
        self.recon_count    = 0
        self.total_count    = 0

        self.valid = measurements() #measurement object
        self.fault = faults() #measurement object
        self.recon = recons() #measurement object

        self.start_time     = None
        self.valid_start    = False
        self.last_frame_type = 3 #0 = valid, 1 = FAULT, 2 = RECONNECT, 3=Initialize

        self.log_file   = None
        self.log_flag   = False

    def run(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print self.utc_ts() + "Connected to Modem..."
        except Exception as e:
            self.Handle_Connection_Exception(e)

        while (not self._stop.isSet()):
            if self.connected == True: 
                for l in self.readlines():
                    #print self.utc_ts(), l
                    self.Decode_Frame(l, date.utcnow())
            elif self.connected == False:
                #print "Disconnected from modem..."
                time.sleep(1)
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
                    self.sock.connect((self.ip, self.port))
                    self.connected = True
                    print self.utc_ts() + "Connected to Modem..."
                except Exception as e:
                    self.Handle_Connection_Exception(e)
        sys.exit()

    def update_log(self, data, ts):
        self.log_f = open(self.log_file, 'a')
        msg = str(ts) + ','
        msg += data
        msg += '\n'
        self.log_f.write(msg)
        self.log_f.close()

    def Decode_Frame(self, line, rx_ts):
        #print str(rx_ts) + "," + line
        #write line to file - TO DO
        if self.log_flag: self.update_log(line, rx_ts)
        data = line.split(",")

        try:
            pkt_id = float(data[2]) #try to type cast field 2 to float.
            self.Decode_Valid(data, rx_ts)
        except:
            if   data[2] == "SERIAL FAULT":
                self.fault.append(data, rx_ts)
                self.last_frame_type = 1
            elif data[2] == "RECONNECTED TO SERIAL PORT":
                self.recon.append(data, rx_ts)
                self.last_frame_type = 2
        #print self.last_frame_type

    def Decode_Valid(self, data, ts):
        self.last_frame_type = 0
        measurement1 = data[0:12] #Extract first measurement
        measurement2 = data[0:3]+data[13:22] #extract second measurement data fields
        
        if self.valid_start == False:
            rx_offset = 0
        elif self.valid_start == True:
            rx_offset = (ts - self.start_time).total_seconds()
            
        self.valid.append(measurement1, ts, rx_offset)
        self.valid.append(measurement2, ts, rx_offset)

    def readlines(self, recv_buffer=4096, delim='\n'):
        #self.lock.acquire()
        buffer = ''
        data = True
        while data:
            data = self.sock.recv(recv_buffer)
            if len(data) == 0: 
                self.connected = False
                print "Disconnected from modem..."
                return
            else:
                buffer += data
                while buffer.find(delim) != -1:
                    line, buffer = buffer.split('\n', 1)
                    #self.lock.release()
                    yield line
        return

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
        self.last_frame_type = 3

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

    def get_last_frame_type(self):
        return self.last_frame_type

    def get_measurements(self):
        return self.valid

    def get_altitude(self):
        return self.valid.alt_ft, self.valid.alt_m

    def get_attitude(self):
        return self.valid.yaw, self.valid.pitch, self.valid.roll

    def get_acceleration(self):
        return self.valid.x_accel, self.valid.y_accel, self.valid.z_accel

    def get_temperature(self):
        return self.valid.temp

    def get_pressure(self):
        return self.valid.pres

    def get_time_tx(self):
        return self.valid.time_tx

    def get_time_rx(self):
        return self.valid.time_rx

    def get_rx_offset(self):
        return self.valid.rx_offset

    def get_last_measurements(self):
        return self.valid.get_last_data()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

