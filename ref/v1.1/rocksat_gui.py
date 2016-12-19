#!/usr/bin/env python

import numpy as np
import sys

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
#from adsb_table import *
from utilities import *
from plot import * 
from mission_clock import *

class main_widget(QtGui.QWidget):
    def __init__(self):
        super(main_widget, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.grid = QtGui.QGridLayout()
        #self.setLayout(self.grid)
        #self.grid.setColumnStretch(0,1)
        #self.grid.setColumnStretch(1,1)

class rocksat_gui(QtGui.QMainWindow):
    def __init__(self, lock):
        super(rocksat_gui, self).__init__()
        #self.resize(1000,1000)
        #self.move(50,50)
        self.setWindowTitle('Rocksat-X 2016 Dashboard, V1.1')
        self.setAutoFillBackground(True)
        #self.ants_static_labels = []
        self.main_window = main_widget()

        self.callback    = None   #Callback accessor function
        self.update_rate = 200    #Feedback Query Auto Update Interval in milliseconds

        self.packet_list    = []
        self.valid_frames   = []
        self.fault_frames   = []
        self.recon_frames   = []

        self.valid_cnt      = 0
        self.fault_cnt      = 0
        self.recon_cnt      = 0
        self.total_cnt      = 0

        self.packet_status  = 3 #0 = valid, 1 = FAULT, 2 = RECONNECT, 3 = Initialization
        #self.use_rx_offset  = False
        
        #Plotting Vectors
        self.time_tx        = []
        self.time_rx        = []
        self.rx_offset      = []
        self.temp           = []
        self.pressure       = []
        self.alt_ft         = []
        self.alt_m          = []
        self.yaw            = []
        self.pitch          = []
        self.roll           = []
        self.x_accel        = []
        self.y_accel        = []
        self.z_accel        = []

        self.initUI()
        self.darken()
        self.setFocus()
        
    def initUI(self): 
        self.initMainWindow()

        self.initMainFrames()
        self.initStatusFrame()
        self.initRTDFrame()
        #self.initTimeFrame()

        self.initTabControl()
        #self.initMainTab()
        self.initPressTab()
        self.initAltitudeTab()
        self.initTempTab()
        self.initAttitudeTab()
        self.initAccelTab()
        
        self.initTimers()
        self.connectSignals()

        #self.show()
        self.showMaximized()

    def initTimers(self):
        self.updateTimer = QtCore.QTimer(self)

    def connectSignals(self):
        self.useRxOffset_cb.stateChanged.connect(self.useRxOffset_event)        
        QtCore.QObject.connect(self.updateTimer, QtCore.SIGNAL('timeout()'), self.updatePackets)
        self.updateTimer.start(self.update_rate)

    def updatePackets(self):
        self.updatePacketStatus()
        self.updatePlots2()
        if self.valid_cnt > 0:
            self.updateRTD()

    def updatePacketStatus(self):
        self.packet_status = self.callback.get_last_frame_type()
        if   self.packet_status == 0:  #Valid
            self.status_lbl.setText("VALID")
            #self.status_lbl.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            self.status_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(0,255,0);}")
        elif self.packet_status == 1:  #Serial Fault
            self.status_lbl.setText("FAULT")
            #self.status_lbl.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            self.status_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(255,0,0);}")
        elif self.packet_status == 2:  #Reconnection
            self.status_lbl.setText("RECONN")
            #self.status_lbl.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            self.status_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(255,255,0);}")
        elif self.packet_status == 3:  #Reconnection
            self.status_lbl.setText("STANDBY")
            #self.status_lbl.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            self.status_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(255,255,0);}")

        [a,b,c,d] = self.callback.get_frame_counts()
        self.total_cnt = a
        self.valid_cnt = b
        self.fault_cnt = c
        self.recon_cnt = d

        statusmsg = ("| Valid Count: %3i | Fault Count: %i | Reconnect Count: %i |" % (self.valid_cnt, self.fault_cnt, self.recon_cnt))
        self.statusBar().showMessage(statusmsg)

        self.total_cnt_lbl.setText(str(self.total_cnt))
        self.valid_cnt_lbl.setText(str(self.valid_cnt))
        self.fault_cnt_lbl.setText(str(self.fault_cnt))
        self.recon_cnt_lbl.setText(str(self.recon_cnt))

    def updatePlots2(self):
        if self.useRxOffset_cb.isChecked() == True:
            x = self.callback.get_rx_offset()
            self.rx_offset = x
        elif self.useRxOffset_cb.isChecked() == False:
            x = self.callback.get_time_tx()
            self.time_tx = x

        try:
            if   self.tabs.currentIndex() == 0: #TEMP
                self.temp = self.callback.get_temperature()
                self.temp_plot.update_figure(x, self.temp)
            elif self.tabs.currentIndex() == 1: #PRESSURE
                self.pressure = self.callback.get_pressure()
                self.press_plot.update_figure(x, self.pressure)
            elif self.tabs.currentIndex() == 2: #ALTITUDE
                self.alt_ft, self.alt_m = self.callback.get_altitude()
                self.alt_ft_plot.update_figure(x, self.alt_ft)
                self.alt_m_plot.update_figure(x, self.alt_m)
            elif self.tabs.currentIndex() == 3: #ATTITUDE
                self.yaw, self.pitch, self.roll = self.callback.get_attitude()
                self.x_att_plot.update_figure(x, self.yaw)
                self.y_att_plot.update_figure(x, self.pitch)
                self.z_att_plot.update_figure(x, self.roll)
            elif self.tabs.currentIndex() == 4:
                self.x_accel, self.y_accel, self.z_accel = self.callback.get_acceleration()
                self.x_accel_plot.update_figure(x, self.x_accel)
                self.y_accel_plot.update_figure(x, self.y_accel)
                self.z_accel_plot.update_figure(x, self.z_accel)
        except Exception as e:
            print self.utc_ts() + "Plotting Error"
            print e

    def updateRTD(self):
        [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o] = self.callback.get_last_measurements()
        self.valid_rx_ts_lbl.setText(str(a))
        self.call_lbl.setText(str(b))
        self.pkt_id_lbl.setText(str(c))
        self.ts_tx_lbl.setText(str(d))
        self.temp_lbl.setText(str(e))
        self.pres_lbl.setText(str(f))
        self.alt_ft_lbl.setText("{:6.2f}".format(g))
        self.alt_m_lbl.setText("{:6.2f}".format(h))
        self.yaw_lbl.setText(str(i))
        self.pitch_lbl.setText(str(j))
        self.roll_lbl.setText(str(k))
        self.x_accel_lbl.setText(str(l))
        self.y_accel_lbl.setText(str(m))
        self.z_accel_lbl.setText(str(n))
        self.rx_offset_lbl.setText(str(o))

    def initMainWindow(self):
        self.setCentralWidget(self.main_window)
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)

        exportAction = QtGui.QAction('Export', self)
        exportAction.setShortcut('Ctrl+E')
        exportAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(exportAction)
  
        self.statusBar().showMessage("| Disconnected | Current Count: 000 |")

    def set_start_time(self, start):
        self.callback.set_start_time(start)
        self.useRxOffset_cb.setEnabled(True)

    def initMainFrames(self):
        #Mission Clock
        self.time_fr = mission_clock(self)
        #Status frame
        self.status_fr = QtGui.QFrame(self)
        self.status_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        #Real Time Data frame
        self.rtd_fr = QtGui.QFrame(self)
        self.rtd_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        #Control Frame
        #self.time_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        #Plot Tab Frames
        self.tab_fr = QtGui.QFrame(self)
        self.tab_fr.setFrameShape(QtGui.QFrame.StyledPanel)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.time_fr)
        vbox.addWidget(self.status_fr)
        vbox.addWidget(self.rtd_fr)
        vbox.addStretch(1)        

        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox)
        #hbox.addStretch(1)
        hbox.addWidget(self.tab_fr)
        self.main_window.setLayout(hbox)

    def initTabControl(self):
        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabPosition(QtGui.QTabWidget.South)

        #self.main_tab = QtGui.QWidget()	
        #self.main_tab.grid = QtGui.QGridLayout()
        #self.tabs.addTab(self.main_tab,"Main")
        #self.main_tab.setAutoFillBackground(True)
        #p = self.main_tab.palette()
        #p.setColor(self.main_tab.backgroundRole(), QtCore.Qt.black)        
        #self.main_tab.setPalette(p)

        self.temp_tab = QtGui.QWidget()	
        self.temp_tab.grid = QtGui.QGridLayout()
        self.tabs.addTab(self.temp_tab,"Temperature")
        self.temp_tab.setAutoFillBackground(True)
        p = self.temp_tab.palette()
        p.setColor(self.temp_tab.backgroundRole(), QtCore.Qt.black)        
        self.temp_tab.setPalette(p)

        self.press_tab = QtGui.QWidget()	
        self.press_tab_grid = QtGui.QGridLayout()
        self.tabs.addTab(self.press_tab,"Pressure")
        self.press_tab.setAutoFillBackground(True)
        p = self.press_tab.palette()
        p.setColor(self.press_tab.backgroundRole(), QtCore.Qt.black)        
        self.press_tab.setPalette(p)

        self.alt_tab = QtGui.QWidget()	
        self.alt_tab_grid = QtGui.QGridLayout()
        self.tabs.addTab(self.alt_tab,"Altitude")
        self.alt_tab.setAutoFillBackground(True)
        p = self.alt_tab.palette()
        p.setColor(self.alt_tab.backgroundRole(), QtCore.Qt.black)        
        self.alt_tab.setPalette(p)

        self.attitude_tab = QtGui.QWidget()	
        self.attitude_tab_grid = QtGui.QGridLayout()
        self.tabs.addTab(self.attitude_tab,"Attitude")
        self.attitude_tab.setAutoFillBackground(True)
        p = self.attitude_tab.palette()
        p.setColor(self.attitude_tab.backgroundRole(), QtCore.Qt.black)        
        self.attitude_tab.setPalette(p)

        self.accel_tab = QtGui.QWidget()	
        self.accel_tab_grid = QtGui.QGridLayout()
        self.tabs.addTab(self.accel_tab,"Acceleration")
        self.accel_tab.setAutoFillBackground(True)
        p = self.accel_tab.palette()
        p.setColor(self.accel_tab.backgroundRole(), QtCore.Qt.black)        
        self.accel_tab.setPalette(p)

        self.tab_fr_grid = QtGui.QGridLayout()
        self.tab_fr.setLayout(self.tab_fr_grid)
        self.tab_fr_grid.addWidget(self.tabs)

    def useRxOffset_event(self):
        if self.useRxOffset_cb.isChecked() == True:
            x_lbl = 'RX Time Offset [s]'
            color = 'r'
        elif self.useRxOffset_cb.isChecked() == False:
            x_lbl = 'TX Time Offset [s]'
            color = 'b'

        self.temp_plot.set_label_x(x_lbl)
        self.temp_plot.set_color(color)
        self.press_plot.set_label_x(x_lbl)
        self.press_plot.set_color(color)
        self.alt_ft_plot.set_label_x(x_lbl)
        self.alt_ft_plot.set_color(color)
        self.alt_m_plot.set_label_x(x_lbl)
        self.alt_m_plot.set_color(color)
        self.x_att_plot.set_label_x(x_lbl)
        self.x_att_plot.set_color(color)
        self.y_att_plot.set_label_x(x_lbl)
        self.y_att_plot.set_color(color)
        self.z_att_plot.set_label_x(x_lbl)
        self.z_att_plot.set_color(color)
        self.x_accel_plot.set_label_x(x_lbl)
        self.x_accel_plot.set_color(color)
        self.y_accel_plot.set_label_x(x_lbl)
        self.y_accel_plot.set_color(color)
        self.z_accel_plot.set_label_x(x_lbl)
        self.z_accel_plot.set_color(color)


    def initTempTab(self):
        self.temp_plot = MyDynamicMplCanvas(self.temp_tab, width=10, height=1, dpi=70, )
        x_lbl = 'TX Time Offset [s]'
        y_lbl = 'Temperature [C]'
        self.temp_plot.set_labels(x_lbl, y_lbl)
        self.temp_tab_grid = QtGui.QGridLayout()
        self.temp_tab_grid.addWidget(self.temp_plot)
        self.temp_tab.setLayout(self.temp_tab_grid)

    def initPressTab(self):
        self.press_plot = MyDynamicMplCanvas(self.press_tab, width=2, height=1, dpi=70, )
        x_lbl = 'TX Time Offset [s]'
        y_lbl = 'Pressure [mbar]'
        self.press_plot.set_labels(x_lbl, y_lbl)
        self.press_tab_grid = QtGui.QGridLayout()
        self.press_tab_grid.addWidget(self.press_plot)
        self.press_tab.setLayout(self.press_tab_grid)

    def initAltitudeTab(self):
        self.alt_ft_plot = MyDynamicMplCanvas(self.alt_tab, width=2, height=1, dpi=70, )
        self.alt_m_plot = MyDynamicMplCanvas(self.alt_tab, width=2, height=1, dpi=70, )
        x_lbl = 'TX Time Offset [s]'
        y1_lbl = 'Altitude [ft]'
        y2_lbl = 'Altitude [m]'
        self.alt_ft_plot.set_labels(x_lbl, y1_lbl)
        self.alt_m_plot.set_labels(x_lbl, y2_lbl)
        self.alt_tab_grid = QtGui.QGridLayout()
        self.alt_tab_grid.addWidget(self.alt_ft_plot)
        self.alt_tab_grid.addWidget(self.alt_m_plot)
        self.alt_tab.setLayout(self.alt_tab_grid)

    def initAttitudeTab(self):
        self.x_att_plot = MyDynamicMplCanvas(self.attitude_tab, width=2, height=.5, dpi=70, )
        self.y_att_plot = MyDynamicMplCanvas(self.attitude_tab, width=2, height=.5, dpi=70, )
        self.z_att_plot = MyDynamicMplCanvas(self.attitude_tab, width=2, height=.5, dpi=70, )
        x_lbl = 'TX Time Offset [s]'
        y1_lbl = 'Yaw [deg]'
        y2_lbl = 'Pitch [deg]'
        y3_lbl = 'Roll [deg]'
        self.x_att_plot.set_labels(x_lbl, y1_lbl)
        self.y_att_plot.set_labels(x_lbl, y2_lbl)
        self.z_att_plot.set_labels(x_lbl, y3_lbl)

        self.attitude_tab_grid = QtGui.QGridLayout()
        self.attitude_tab_grid.addWidget(self.x_att_plot)
        self.attitude_tab_grid.addWidget(self.y_att_plot)
        self.attitude_tab_grid.addWidget(self.z_att_plot)
        self.attitude_tab.setLayout(self.attitude_tab_grid)

    def initAccelTab(self):
        self.x_accel_plot = MyDynamicMplCanvas(self.accel_tab, width=2, height=1, dpi=70, )
        self.y_accel_plot = MyDynamicMplCanvas(self.accel_tab, width=2, height=1, dpi=70, )
        self.z_accel_plot = MyDynamicMplCanvas(self.accel_tab, width=2, height=1, dpi=70, )
        x_lbl = 'TX Time Offset [s]'
        y1_lbl = 'X Acceleration [g]'
        y2_lbl = 'Y Acceleration [g]'
        y3_lbl = 'Z Acceleration [g]'
        self.x_accel_plot.set_labels(x_lbl, y1_lbl)
        self.y_accel_plot.set_labels(x_lbl, y2_lbl)
        self.z_accel_plot.set_labels(x_lbl, y3_lbl)
        self.accel_tab_grid = QtGui.QGridLayout()
        self.accel_tab_grid.addWidget(self.x_accel_plot)
        self.accel_tab_grid.addWidget(self.y_accel_plot)
        self.accel_tab_grid.addWidget(self.z_accel_plot)
        self.accel_tab.setLayout(self.accel_tab_grid)
    
    def initStatusFrame(self):
        fr_lbl = QtGui.QLabel("Packet Status:")
        fr_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        fr_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; text-decoration:underline; color:rgb(255,255,255);}")
        fr_lbl.setFixedHeight(25)
        self.status_lbl = QtGui.QLabel("NOCONN")
        self.status_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.status_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; color:rgb(255,255,255);}")
        self.status_lbl.setFixedWidth(90)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(fr_lbl)
        hbox1.addWidget(self.status_lbl)

        lbl = QtGui.QLabel("Total Count:")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(125)
        self.total_cnt_lbl = QtGui.QLabel("0")
        self.total_cnt_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.total_cnt_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.total_cnt_lbl.setFixedWidth(80)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(lbl)
        hbox2.addWidget(self.total_cnt_lbl)

        lbl = QtGui.QLabel("Valid Count:")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(125)
        self.valid_cnt_lbl = QtGui.QLabel("0")
        self.valid_cnt_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.valid_cnt_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.valid_cnt_lbl.setFixedWidth(80)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addWidget(lbl)
        hbox3.addWidget(self.valid_cnt_lbl)

        lbl = QtGui.QLabel("Fault Count:")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(125)
        self.fault_cnt_lbl = QtGui.QLabel("0")
        self.fault_cnt_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fault_cnt_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.fault_cnt_lbl.setFixedWidth(80)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.addWidget(lbl)
        hbox4.addWidget(self.fault_cnt_lbl)

        lbl = QtGui.QLabel("Reconnect Count:")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(125)
        self.recon_cnt_lbl = QtGui.QLabel("0")
        self.recon_cnt_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.recon_cnt_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.recon_cnt_lbl.setFixedWidth(80)
        hbox5 = QtGui.QHBoxLayout()
        hbox5.addWidget(lbl)
        hbox5.addWidget(self.recon_cnt_lbl)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        #vbox.addLayout(hbox6)
        #vbox.addLayout(hbox7)
        #vbox.addLayout(hbox8)
        #vbox.addLayout(hbox9)
        #vbox.addLayout(hbox10)
        #vbox.addLayout(hbox11)
        vbox.addStretch(1)
        self.status_fr.setLayout(vbox)

   

    def initRTDFrame(self):
        lbl_width = 125
        val_width = 80

        fr_lbl = QtGui.QLabel("Real-Time Data")
        fr_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        fr_lbl.setStyleSheet("QLabel {font-size:18px; font-weight:bold; text-decoration:underline; color:rgb(255,255,255);}")
        fr_lbl.setFixedHeight(25)

        lbl = QtGui.QLabel("Callsign: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.call_lbl = QtGui.QLabel("XXXXXX")
        self.call_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.call_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.call_lbl.setFixedWidth(val_width)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(lbl)
        hbox1.addWidget(self.call_lbl)

        lbl = QtGui.QLabel("Packet ID: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.pkt_id_lbl = QtGui.QLabel("XXX")
        self.pkt_id_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pkt_id_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.pkt_id_lbl.setFixedWidth(val_width)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(lbl)
        hbox2.addWidget(self.pkt_id_lbl)

        lbl = QtGui.QLabel("TX Time Stamp [s]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.ts_tx_lbl = QtGui.QLabel("XXX")
        self.ts_tx_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.ts_tx_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.ts_tx_lbl.setFixedWidth(val_width)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addWidget(lbl)
        hbox3.addWidget(self.ts_tx_lbl)

        lbl = QtGui.QLabel("Temperature [C]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.temp_lbl = QtGui.QLabel("XXX")
        self.temp_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.temp_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.temp_lbl.setFixedWidth(val_width)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.addWidget(lbl)
        hbox4.addWidget(self.temp_lbl)

        lbl = QtGui.QLabel("Pressure [mbar]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.pres_lbl = QtGui.QLabel("XXX")
        self.pres_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pres_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.pres_lbl.setFixedWidth(val_width)
        hbox5 = QtGui.QHBoxLayout()
        hbox5.addWidget(lbl)
        hbox5.addWidget(self.pres_lbl)

        lbl = QtGui.QLabel("Altitude [ft]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.alt_ft_lbl = QtGui.QLabel("XXX")
        self.alt_ft_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.alt_ft_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.alt_ft_lbl.setFixedWidth(val_width)
        hbox5_1 = QtGui.QHBoxLayout()
        hbox5_1.addWidget(lbl)
        hbox5_1.addWidget(self.alt_ft_lbl)

        lbl = QtGui.QLabel("Altitude [m]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.alt_m_lbl = QtGui.QLabel("XXX")
        self.alt_m_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.alt_m_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.alt_m_lbl.setFixedWidth(val_width)
        hbox5_2 = QtGui.QHBoxLayout()
        hbox5_2.addWidget(lbl)
        hbox5_2.addWidget(self.alt_m_lbl)

        lbl = QtGui.QLabel("Yaw [deg]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.yaw_lbl = QtGui.QLabel("XXX")
        self.yaw_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.yaw_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.yaw_lbl.setFixedWidth(val_width)
        hbox6 = QtGui.QHBoxLayout()
        hbox6.addWidget(lbl)
        hbox6.addWidget(self.yaw_lbl)

        lbl = QtGui.QLabel("Pitch [deg]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.pitch_lbl = QtGui.QLabel("XXX")
        self.pitch_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pitch_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.pitch_lbl.setFixedWidth(val_width)
        hbox7 = QtGui.QHBoxLayout()
        hbox7.addWidget(lbl)
        hbox7.addWidget(self.pitch_lbl)

        lbl = QtGui.QLabel("Roll [deg]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.roll_lbl = QtGui.QLabel("XXX")
        self.roll_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.roll_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.roll_lbl.setFixedWidth(val_width)
        hbox8 = QtGui.QHBoxLayout()
        hbox8.addWidget(lbl)
        hbox8.addWidget(self.roll_lbl)

        lbl = QtGui.QLabel("Accel-X [g]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.x_accel_lbl = QtGui.QLabel("XXX")
        self.x_accel_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.x_accel_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.x_accel_lbl.setFixedWidth(val_width)
        hbox9 = QtGui.QHBoxLayout()
        hbox9.addWidget(lbl)
        hbox9.addWidget(self.x_accel_lbl)

        lbl = QtGui.QLabel("Accel-Y [g]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.y_accel_lbl = QtGui.QLabel("XXX")
        self.y_accel_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.y_accel_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.y_accel_lbl.setFixedWidth(val_width)
        hbox10 = QtGui.QHBoxLayout()
        hbox10.addWidget(lbl)
        hbox10.addWidget(self.y_accel_lbl)

        lbl = QtGui.QLabel("Accel-Z [g]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.z_accel_lbl = QtGui.QLabel("XXX")
        self.z_accel_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.z_accel_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.z_accel_lbl.setFixedWidth(val_width)
        hbox11 = QtGui.QHBoxLayout()
        hbox11.addWidget(lbl)
        hbox11.addWidget(self.z_accel_lbl)

        lbl = QtGui.QLabel("RX Offset [s]: ")
        lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.rx_offset_lbl = QtGui.QLabel("XXX")
        self.rx_offset_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.rx_offset_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.rx_offset_lbl.setFixedWidth(val_width)
        hbox12 = QtGui.QHBoxLayout()
        hbox12.addWidget(lbl)
        hbox12.addWidget(self.rx_offset_lbl)

        lbl = QtGui.QLabel("RX Time Stamp: ")
        lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        lbl.setFixedWidth(lbl_width)
        self.valid_rx_ts_lbl = QtGui.QLabel("")
        self.valid_rx_ts_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.valid_rx_ts_lbl.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        self.valid_rx_ts_lbl.setFixedWidth(200)
        vbox12 = QtGui.QVBoxLayout()
        vbox12.addWidget(lbl)
        vbox12.addWidget(self.valid_rx_ts_lbl)

        self.useRxOffset_cb = QtGui.QCheckBox("Use RX Offset")  
        self.useRxOffset_cb.setStyleSheet("QCheckBox { background-color:rgb(0,0,0); color:rgb(255,0,0); }")
        self.useRxOffset_cb.setChecked(False)
        self.useRxOffset_cb.setEnabled(False)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(fr_lbl)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox5_1)
        vbox.addLayout(hbox5_2)
        vbox.addLayout(hbox6)
        vbox.addLayout(hbox7)
        vbox.addLayout(hbox8)
        vbox.addLayout(hbox9)
        vbox.addLayout(hbox10)
        vbox.addLayout(hbox11)
        vbox.addLayout(hbox12)
        vbox.addLayout(vbox12)
        vbox.addWidget(self.useRxOffset_cb)
        vbox.addStretch(1)

        self.rtd_fr.setLayout(vbox)

    def set_callback(self, callback):
        self.callback = callback

    def darken(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.black)
        palette.setColor(QtGui.QPalette.WindowText,QtCore.Qt.black)
        palette.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
        self.setPalette(palette)

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | "

        
def main():
    app = QtGui.QApplication(sys.argv)
    ex = funcube_tlm_gui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
