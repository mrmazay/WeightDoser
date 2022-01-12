# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import serial, serial.tools.list_ports
import time


class Balance(QObject):

        weightReady = pyqtSignal()
        bSer = serial
        curWeight = 0.000
        isStable = False
        isZero = False
        isNegative = False
        connected = False

        @pyqtSlot()
        def __init__(self):
            super(Balance, self).__init__()
            self.working = True

        def getCurWeight(self):
            self.isNegative = False
            self.isStable = False
            self.isZero = False         # ????????????????????????????????????????
            self.bSer.write("SUI\r\n".encode())
            resp = self.bSer.readline().decode()
            print(resp)
            if len(resp) == 21:
                arr = resp.split()
                print(arr)
                if resp[:3] == "SUI":
                   if resp[4:4] == " ":
                       self.isStable = True
                   if resp[6:6] == "-":
                       self.isNegative = True
                   self.curWeight = float(resp[7:15].split()[0])
                   self.weightReady.emit()
                else:
                    print("Error getCurWeight")
                    return -1
            else:
                print("Error getCurWeight")
                return -1

            def setZero(self):
                self.working = False
                self.bSer.write("Z\r\n".encode('utf-8'))
                resp = self.bSer.readline().decode()
                print(resp)
                if resp[0] == "Z" and resp[2] == "A":
                    resp = self.bSer.read(5).decode()
                    print(resp)
                    if resp[0] == "Z" and resp[2] == 'D':
                        self.isZero = True
                        self.getCurWeight()
                        return 1
                    else:
                        return -1

            def updateLoop(self):
                while self.working:
                    self.getCurWeight()
                    time.sleep(1)
                self.working = True
