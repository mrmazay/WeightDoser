# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import serial, serial.tools.list_ports
import time


class Doser(QObject):
    # enable = 0
     speed = 0
    # reverce = 0
    # stepCount = 0
     ser = serial
     packet = bytearray()
     connected = False

     @pyqtSlot()
     def __init__(self):
         super(Doser, self).__init__()
         self.working = False

     def connect(self,port):
         self.packet = bytearray()
         self.packet.clear()
         self.packet.append(90)
         self.packet.append(13)
         self.packet.append(10)
         try:
             self.ser = serial.Serial(port, 19200, timeout=3)
             self.ser.write("Z\r\n".encode())
             time.sleep(1)
             resp = self.ser.read(1)
             if resp == b'D':
                 self.connected = True
                 return 1
             else:
                 self.connected = False
                 self.ser.close
                 return 0
         except (OSError, serial.SerialException):
                 pass


     def setSpeed(self, speed):
         self.speed = speed
         self.packet.clear()
         self.packet.append(60)
         self.packet.extend(str(speed).encode())
         self.packet.append(62)
         self.ser.write(self.packet)
         #resp = self.ser.readline().decode()
         #req=self.packet.decode()
         return "REQ:"

