#!/usr/bin/env python
import sys
import serial, serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import design  # Это наш конвертированный файл дизайна
import time


class Doser(QObject):
    enable = 0
    speed = 0
    reverce = 0
    stepCount = 0

    @pyqtSlot()
    def __init__(self):
        super(Doser, self).__init__()


class Balance(QObject):
    weightReady = pyqtSignal()
    bSer = serial
    curWeight = 0.000
    isStable = False
    isZero = False
    isNegative = False
    Connected = False

    @pyqtSlot()
    def __init__(self):
        super(Balance, self).__init__()

    def getCurWeight(self):
        self.isNegative = False
        self.isStable = False
        self.isZero = False         #  ????????????????????????????????????????
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
                return 1
            else:
                return -1

    def updateLoop(self):
        while self.working:
            self.getCurWeight()


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    ser = serial

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.Balance = Balance()
        self.thread = QThread()  # a new thread to run our background tasks in
        self.Balance.moveToThread(self.thread)
        self.Balance.weightReady.connect(self.updGUI)
        # self.Balance.bSer = serial.Serial(self.lineEdit_4.text(), 9600, timeout=3)
        self.pushButton.clicked.connect(self.start_loop)
        self.pushButton_2.clicked.connect(self.stop_loop)
       # self.Balance.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
       # self.Balance.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
       # self.Balance.finished.connect(self.Balance.deleteLater)  # have worker mark itself for deletion
       # self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
                # make sure those last two are connected to themselves or you will get random crashes
        self.thread.start()

    def updGUI(self):
        self.label_11.setText(str(self.Balance.curWeight))

    def start_loop(self):
        self.textEdit.append("Opening port")
        self.Balance.bSer = serial.Serial(self.lineEdit_4.text(), 9600, timeout=3)
        # self.ser = serial.Serial(self.lineEdit_4.text(), 9600, timeout=3)

    def stop_loop(self):
        self.textEdit.append("Closing port...")
        self.Balance.bSer.close()
        # self.ser.close()

    def onIntReady(self, i):
        self.textEdit.append("{}".format(i))
        arr = i.split()
        self.label_11.setText(arr[1]+' '+arr[2])

    def on_pushButton_6_clicked(self):
        self.Balance.setZero()

    def on_pushButton_5_clicked(self):
        self.Balance.getCurWeight()
        self.label_11.setText(str(self.Balance.curWeight))

    def on_pushButton_7_clicked(self):
        self.Balance.working = True
        self.Balance.updateLoop()


    def on_pushButton_8_clicked(self):
        self.Balance.working = False


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
