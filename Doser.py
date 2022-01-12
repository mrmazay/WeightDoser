# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import serial, serial.tools.list_ports
import time


class Doser(QObject):
    # enable = 0
    # speed = 0
    # reverce = 0
    # stepCount = 0
     dSer = serial
     packet = bytearray()

     @pyqtSlot()
     def __init__(self):
         super(Doser, self).__init__()
         self.working = True

     def dose(self, stepCount):
         self.packet.clear()
         self.packet.append(stepCount)
         self.dSer.write(self.packet)

