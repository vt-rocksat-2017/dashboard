#!/usr/bin/env python
##################################################
# Title: Gimbal Tracking, Telemetry. and Control Code
# Author: Zachary James Leffke
# Description: 
#   Code for controlling the TTC interface for the gimbal
# Generated: May 12, 2014
##################################################

import logging
import threading
import socket
import datetime as dt
import os

class MyFormatter(logging.Formatter):
    #Overriding formatter for datetime
    converter=dt.datetime.utcfromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class Data_Logger(threading.Thread):
    def __init__(self, name=None, parent=None):
        threading.Thread.__init__(self, name='ttc_logger')
        self._stop  = threading.Event()
        self.lock   = threading.Lock()
        self.startup_ts = startup_ts
        self.parent=parent
        self.logger=None
        self.ttc_data = {}
        self.ttc_sentence = ""
        self.init_logger()
        
    def run(self):
        while (not self._stop.isSet()):
            time.sleep(10)
        
    def log_ttc(self, sentence):
        self.logger.info(sentence)

    def init_logger(self):
        self.log_file = "ttc_{:s}.log".format(self.startup_ts)
        self.log_path = os.getcwd() + '/log/' + self.log_file
        self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.INFO)
        self.hdlr  = logging.FileHandler(self.log_path)
        self.logger.addHandler(self.hdlr)
        self.formatter = MyFormatter(fmt='%(asctime)s UTC - %(threadName)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S.%f')
        self.hdlr.setFormatter(self.formatter)
        self.logger.info('Logger Initialized')
        self.logger.info('TTC SENTENCE FORMAT: ')
        self.logger.info('    GPS: $,date, num_sats, mode, lat, lon, alt [m], spd, trk, climb')
        self.logger.info('    IMU: #,roll,pitch,yaw,temp,sys_cal,accel_cal,gyro_cal,mag_cal')
        self.logger.info('  RAZEL: %,gimbal_state,rho_mag,az,el')

    def stop(self, caller=None):
        if caller:
            print "killing", self.name
            self.logger.warning('Terminating MD01 Logger Thread at request of: {:s}'.format(str(caller)))
        else:
            self.logger.warning('Terminating MD01 Logger Thread from unknown caller')
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
