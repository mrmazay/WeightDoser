#!/usr/bin/env python
import sys
import serial, serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import design  # Это наш конвертированный файл дизайна
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


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    ser = serial

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
# Перенести на кнопку подключения!!!!!!!!!!!!
        self.Balance = Balance()
        self.Doser = Doser()
        self.dosThread = QThread()
        self.thread = QThread()  # a new thread to run our background tasks in
        self.Balance.moveToThread(self.thread)
        self.Doser.moveToThread(self.dosThread)
        self.textEdit.append("Opening balance port")
        self.Balance.bSer = serial.Serial('/dev/ttyUSB0', 19200, timeout=3)
        self.Doser.dSer = serial.Serial('/dev/ttyUSB1', 19200, timeout=3)
        self.Balance.weightReady.connect(self.updGUI)
        self.pushButton.clicked.connect(self.Balance.updateLoop)
        self.pushButton_2.clicked.connect(self.stop_loop)
       # self.Balance.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
       # self.Balance.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
       # self.Balance.finished.connect(self.Balance.deleteLater)  # have worker mark itself for deletion
       # self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
                # make sure those last two are connected to themselves or you will get random crashes
        self.thread.start()

    def updGUI(self):
        self.label.setText("Working")
        self.label_11.setText(str(self.Balance.curWeight))
        fill = self.Balance.curWeight*100/float(self.lineEdit.text())
        self.textEdit.append(str(fill))
        self.Doser.dose(95-int(fill))

    def stop_loop(self):
        self.Balance.working = False
        self.label.setText("IDLE")

    def on_pushButton_6_clicked(self):
        if self.Balance.working is False:
            self.label_11.setText("---.---")
            self.label.setText("Zeroing")
            self.Balance.setZero()
        else: self.textEdit.append("Stop dosing first!!")

    def on_pushButton_5_clicked(self):
        if self.Balance.working is False:
            self.Balance.getCurWeight()
        else: self.textEdit.append("Stop dosing first!!")

    def on_pushButton_8_clicked(self):
        fill = self.Balance.curWeight*100/float(self.lineEdit.text())
        self.textEdit.append(str(fill))
        self.Doser.dose(200*(100-int(fill))/100)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
