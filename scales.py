# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import serial, serial.tools.list_ports
import time


class Balance(QObject):

        weightReady = pyqtSignal()
        ser = serial
        curWeight = 0.000
        isStable = False
        isZero = False
        isNegative = False
        connected = False

        @pyqtSlot()
        def __init__(self):
            super(Balance, self).__init__()
            self.working = False

        def connect(self,port):
            packet = bytearray()
            packet.clear()
            packet.append(90)
            packet.append(13)
            packet.append(10)
            try:
                self.ser = serial.Serial(port, 19200, timeout=3)
                self.ser.write("Z\r\n".encode())
                time.sleep(1)
                resp = self.ser.read(1)
                if resp == b'Z':
                    self.connected = True
                    return 1
                else:
                    self.connected = False
                    self.ser.close
                    return 0
            except (OSError, serial.SerialException):
                    pass



        def update(self):
            if self.connected:
                self.isNegative = False
                self.isStable = False
                self.isZero = False         # ????????????????????????????????????????
                self.ser.reset_input_buffer()
                self.ser.write("SUI\r\n".encode())
                resp = self.ser.readline().decode()
                # print(resp)
                if len(resp) == 21:
                    arr = resp.split()
                    print(arr)
                    if resp[:3] == "SUI":
                       if resp[4:4] == " ":
                           self.isStable = True
                       if resp[6:6] == "-":
                           self.isNegative = True
                       self.curWeight = float(resp[7:15].split()[0])
                       if self.isNegative : self.curWeight *= -1
                       self.weightReady.emit()
                    else:
                        print("Error: Not SUI answer")
                        return -1
                else:
                    print("Error: invalid answer packet length")
                    return -1


        def tare(self):
                self.working = False
                self.ser.write("T\r\n".encode('utf-8'))
                resp = self.ser.readline().decode()
                print(resp)
                if resp[0] == "T" and resp[2] == "A":
                    resp = self.ser.read(5).decode()
                    print(resp)
                    if resp[0] == "T" and resp[2] == 'D':
                        self.isZero = True
                        return 1
                    else:
                        return -1

        def setZero(self):
                self.working = False
                self.ser.write("Z\r\n".encode('utf-8'))
                resp = self.ser.readline().decode()
                print(resp)
                if resp[0] == "Z" and resp[2] == "A":
                    resp = self.ser.read(5).decode()
                    print(resp)
                    if resp[0] == "Z" and resp[2] == 'D':
                        self.isZero = True
                        return 1
                    else:
                        return -1

        def updateLoop(self):
                while 1:
                    if self.connected and self.working:
                        self.update()
                        # time.sleep(1)
                # self.working = True
