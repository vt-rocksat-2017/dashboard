#!/usr/bin/env python
#########################################
#   Title: Rocksat Data Server Class    #
# Project: Rocksat                      #
# Version: 1.0                          #
#    Date: July 06, 2016                #
#  Author: Zach Leffke, KJ4QLP          #
# Comment: Initial Version              # 
#########################################

from __future__ import unicode_literals
import sys
import os
#import random
#from matplotlib.backends import qt_compat
#use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE

#if use_pyside:
#    from PySide import QtGui, QtCore
#else:
from PyQt4 import QtGui, QtCore
from numpy import arange, sin, pi
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        
        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyDynamicMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        #print args
        self.xd = []
        self.yd = []
        self.x_lbl = None
        self.y_lbl = None
        self.color = 'b'

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def set_labels(self, x, y):
        self.x_lbl = x
        self.y_lbl = y

    def set_label_x(self, x):
        self.x_lbl = x

    def set_label_y(self, y):
        self.y_lbl = y

    def set_color(self, color):
        self.color = color

    def update_figure(self, x, y):
        self.xd = x
        self.yd = y
        self.axes.plot(self.xd, self.yd, self.color)
        self.axes.xaxis.grid(True)
        self.axes.yaxis.grid(True)
        self.axes.set_xlabel(self.x_lbl)
        self.axes.set_ylabel(self.y_lbl)
        self.axes.get_yaxis().get_major_formatter().set_useOffset(False)
        self.draw()
