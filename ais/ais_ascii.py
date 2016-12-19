#!/usr/bin/env python
from math import *
import string
import binascii
from bitarray import bitarray


def ais_to_bitarray(data):
    #print data
    ba = bitarray()
    for ch in data:
        print ch


class ais_msg_123(object):
    def __init__(self, data):
        #Message 1,2,3 - Position Report
        self.msg_id     = None  # Message Identifier
        self.rpt_ind    = None  # Repeater Indicator
        self.mmsi       = None  # USer ID, MMSI
        self.nav_stat   = None  # Navigation Status
        self.turn_rate  = None  # Rate of Turn ROTAIS
        self.sog        = None  # SOG
        self.pos_acc    = None  # Position Accuracy
        self.lon        = None  # Longitude
        self.lat        = None  # Latitude
        self.cog        = None  # COG
        self.heading    = None  # True Heading
        self.time_stamp = None  # Time Stamp
        self.smi        = None  # Special Maneuver Indicator
        self.spare      = None  # Spare
        self.raim_flag  = None  # RAIM Flag
        #Communication State
        self.sync_state     = None  # Sync State
        self.slot_timeout   = None  # Slot Timeout
        self.slot_num       = None  # Slot Number

class ais_msg_4(object):
    def __init__(self, data):
        #Message 4 - Base Station Report
        self.msg_id     = None  # Message Identifier
        self.rpt_ind    = None  # Repeater Indicator
        self.mmsi       = None  # USer ID, MMSI
        self.year       = None  # UTC Year
        self.month      = None  # UTC Month
        self.day        = None  # UTC Day
        self.hour       = None  # UTC Hour
        self.minute     = None  # UTC Minute
        self.second     = None  # UTC Second
        self.pos_acc    = None  # Position Accuracy
        self.lon        = None  # Longitude
        self.lat        = None  # Latitude
        self.epfd_type  = None  # EPFD Type
        self.spare      = None  # Spare
        self.raim_flag  = None  # RAIM Flag
        #Communication State
        self.sync_state     = None  # Sync State
        self.slot_timeout   = None  # Slot Timeout
        self.slot_num       = None  # Slot Number

class ais_msg_21(object):
    def __init__(self, data):
        #Aids to Navigation Report
        self.msg_id     = None  # Message Identifier
        self.rpt_ind    = None  # Repeater Indicator
        self.mmsi       = None  # USer ID, MMSI
        self.nav_type   = None  # Navigation Type    
        self.name       = None  # Name
        self.pos_acc    = None  # Position Accuracy
        self.lon        = None  # Longitude
        self.lat        = None  # Latitude
        self.dim        = None  # Dimensions
        self.epfd_type  = None  # EPFD Type
        self.utc_ts     = None  # UTC Time Stamp
        self.pos_ind    = None  # Position Indicator On/Off
        self.aton_reg   = None  # A to N Reg App
        self.raim_stat  = None  # RAIM Status
        self.virt_flag  = None  # Virtual Flag
        self.mode_ind   = None  # Mode Indicator
        self.spare      = None  # Spare
        self.ext_name   = None  # Ext Name
        self.stuff_bits = None  # Stuff Bits
