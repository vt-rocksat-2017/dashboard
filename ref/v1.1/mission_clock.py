#!/usr/bin/env python
#########################################
#   Title: Mission Clock Widget         #
# Project: Rocksat                      #
# Version: 1.0                          #
#    Date: July 11, 2016                #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: Initial Version              # 
#########################################

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt

import PyQt4.Qwt5 as Qwt

from datetime import datetime as date
from numpy import arange, sin, pi
import numpy as np

class mission_clock(QtGui.QFrame):
    def __init__(self, parent=None):
        super(mission_clock, self).__init__()

        self.parent = parent
        self.update_rate    = 10 #milliseconds, update interval for mision clock
        self.hold           = True #Indicates status of mission clock HOLD, 
        self.start_time     = None #datetime object, UTC time that clock is started

        self.now            = date.utcnow()
        self.start_time     = None #datetime object, timestamp of start of mission clock.
        self.mission_clock  = 0 #cumulative mission clock

        self.initUI()

    def initUI(self):
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.initWidgets()
        self.initTimer()
        self.connectSignals()

    def initWidgets(self):
        fr_lbl = QtGui.QLabel("Mission Clock:")
        fr_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        fr_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; text-decoration:underline; color:rgb(255,255,255);}")
        fr_lbl.setFixedHeight(25)
        self.mission_time_lbl = QtGui.QLabel('+000.00')
        self.mission_time_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.mission_time_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(255,255,0);}")
        self.mission_time_lbl.setFixedWidth(80)
        hbox0 = QtGui.QHBoxLayout()
        hbox0.addWidget(fr_lbl)
        hbox0.addWidget(self.mission_time_lbl)

        lbl = QtGui.QLabel("Current Date [UTC]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(140)
        self.cur_date_lbl = QtGui.QLabel('')
        self.cur_date_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.cur_date_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.cur_date_lbl.setFixedWidth(80)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(lbl)
        hbox1.addWidget(self.cur_date_lbl)

        lbl = QtGui.QLabel("Current Time [UTC]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(140)
        self.cur_time_lbl = QtGui.QLabel('')
        self.cur_time_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.cur_time_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.cur_time_lbl.setFixedWidth(80)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(lbl)
        hbox2.addWidget(self.cur_time_lbl)

        self.StartButton = QtGui.QPushButton("Start")

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addLayout(hbox0)
        self.vbox.addLayout(hbox1)
        self.vbox.addLayout(hbox2)
        self.vbox.addWidget(self.StartButton)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)        


    def initTimer(self):
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.setInterval(self.update_rate)
        self.updateTimer.start()

    def connectSignals(self):
        self.StartButton.clicked.connect(self.StartButtonClicked)
        QtCore.QObject.connect(self.updateTimer, QtCore.SIGNAL('timeout()'), self.updateClock)


    def updateClock(self):
        self.now = date.utcnow()
        self.cur_date_lbl.setText('{:%Y-%m-%d}'.format(self.now))
        self.cur_time_lbl.setText('{:%H:%M:%S}'.format(self.now))

        if self.hold == False:
            self.mission_clock = (self.now - self.start_time).total_seconds()
            self.mission_time_lbl.setText('{:+3.2f}'.format(self.mission_clock))

    def StartButtonClicked(self):
        self.start_time = date.utcnow()
        self.hold = False
        self.mission_time_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(0,255,0);}")
        self.parent.set_start_time(self.start_time)
        self.StartButton.setEnabled(False)
    
    





