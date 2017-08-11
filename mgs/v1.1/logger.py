#!/usr/bin/env python2

# Logger utilities

import math, sys, os, time, struct, traceback, binascii, logging
import datetime as dt

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


def setup_logger(rx_id, log_name, startup_ts, level=logging.INFO):
    l = logging.getLogger(log_name)
    log_file = "{:s}_{:s}_{:s}.log".format(rx_id.upper(), log_name.upper(), startup_ts)
    log_path = '/captures/rocksat/' + log_file
    formatter = MyFormatter(fmt='%(asctime)s UTC,%(message)s',datefmt='%Y-%m-%d %H:%M:%S.%f')
    #fileHandler = logging.FileHandler(log_path, mode='w')
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(formatter)
    #streamHandler = logging.StreamHandler()
    #streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    l.info('Logger Initialized')
    #l.addHandler(streamHandler) 
    return fileHandler

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        #print uptime_seconds
        return uptime_seconds
        #uptime_string = str(timedelta(seconds = uptime_seconds))
