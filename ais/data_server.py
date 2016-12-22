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
import json


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

        self.ais_msgs       = []

        self.frag_flag      = False #Fragmented message flag
        self.frag_count     = 0     #number of message fragments
        self.frag_buff      = ""    #Message buffer for multi-fragment messages


        #---------OLD VAriables, may still need some------------
        #self.valid = measurements() #measurement object
        #self.fault = faults() #measurement object
        #self.recon = recons() #measurement object

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
                for ts,l in self.readlines():
                    #print ts, l
                    self.Decode_Frame(ts, l.split(','))
                #data = self.sock.recv(4096)
                #for 
                #print self.utc_ts(), data
                #self.Decode_Frame(data, date.utcnow())
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

    def Decode_Frame(self, ts, data):
        #print str(rx_ts) + "," + line
        if data[0] == "!AIVDM": #legitimate AIS Message
            #print str(ts) + " UTC |", data
            if int(data[1]) > 1:  #fragmented message
                print "message fragmented", data[2]
                if self.frag_flag: #fragment flag set by previous loop
                    self.frag_buff += data[5]
                    if data[1] == data[2]:  #this is last iteration of message
                        self.ais_msgs.append(ais_msg(ts, data[4], self.frag_buff))
                        #print len(self.ais_msgs), self.ais_msgs[-1].ts, self.ais_msgs[-1].chan, self.ais_msgs[-1].msg
                        #print self.ais_msgs[-1].msg_decoded, "\n"
                        self.frag_buff = ""
                        self.frag_flag = False
                        self.frag_count = 0
                else:
                    self.frag_buff += data[5]
                    self.frag_flag = True
                    self.frag_count = data[1]
            else:  #single line
                self.ais_msgs.append(ais_msg(ts, data[4], data[5]))
                #print len(self.ais_msgs), self.ais_msgs[-1].ts, self.ais_msgs[-1].chan, self.ais_msgs[-1].msg
                #print self.ais_msgs[-1].msg_decoded, "\n"
        if len(self.ais_msgs) > 0:
            print len(self.ais_msgs), self.ais_msgs[-1].ts, self.ais_msgs[-1].chan, self.ais_msgs[-1].msg
            print self.ais_msgs[-1].msg_decoded, "\n"
                
        #print self.ais_msg, len(self.ais_msg)
        #try:
        #    a = ais.decode(self.ais_msg,0)        
            #print a, type(a)
        #    if (a['id'] == 1) or (a['id'] == 2) or (a['id'] == 3): #Position Report
        #        print self.ais_chan, a['id'], a['mmsi'], a['x'], a['y'], a['true_heading']
        #    elif a['id'] ==4: #Base station Report
        #        print self.ais_chan, a['id'], a['x'], a['y'], a['mmsi']
        #    elif a['id'] == 21: #Aids to Navigation
        #        print self.ais_chan, a['id'], a['x'], a['y'], a['mmsi']
        #    elif a['id'] == 18: #Standard Class B CS Position Report
        #       print self.ais_chan, a['id'], a['x'], a['y'], a['mmsi']
        #except Exception as e:
        #    print e
        #self.ais_msgs.append(ais_msg(date.utcnow(), data.split(",")))

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

    def readlines(self, recv_buffer=4096, delim='!'):
        #self.lock.acquire()
        buffer = ''
        data = True
        while data:
            data = self.sock.recv(recv_buffer)
            ts = date.utcnow()
            #print self.utc_ts(), data
            if len(data) == 0: 
                self.connected = False
                print "Disconnected from modem..."
                return
            else:
                buffer += data
                while buffer.find(delim) != -1:
                    line, buffer = buffer.split(delim, 1)
                    #self.lock.release()
                    line = "!" + line
                    yield ts, line.strip("\n")
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

