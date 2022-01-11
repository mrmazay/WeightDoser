#!/usr/bin/env python
import sys, serial, serial.tools.list_ports, warnings
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QThread, pyqtSlot
import design  # Это наш конвертированный файл дизайна
import time


class Balance(QObject):
    bSer = serial
    curWeight =0.000
    isStable = 1
    isZero = 0
    isNegative = 0
    @pyqtSlot()
    def __init__(self):
        super(Balance, self).__init__()

    def getCurWeight(self):
        self.isNegative = 0
        self.isStable = 0
        self.isZero = 0         #  ????????????????????????????????????????
        self.bSer.write("SUI\r\n".encode())
        resp = self.bSer.readline().decode()
        print(resp)
        if len(resp) == 21:
            arr = resp.split()
            print(arr)
            if resp[:3] == "SUI":
               if resp[4:4]==" ":
                   self.isStable = 1
               if resp[6:6]=="-":
                   self.isNegative = 1
               self.curWeight = float(resp[7:15].split()[0])
            else:
                print("Error getCurWeight")
                return -1
        else:
            print("Error getCurWeight")
            return -1

    # def setCurWeight(self,i):
    #   self.currentWeight = i

    def setZero(self):
        self.bSer.write("Z\r\n".encode('utf-8'))
        resp = self.bSer.readline().decode()
        print(resp)
        if resp[0] == "Z" and resp[2] == "A":
            resp = self.bSer.read(5).decode()
            print(resp)
            if resp[0] == "Z" and resp[2] == 'D':
                self.isZero = 1
                return 1
            else:
                return -1


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    ser = serial

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.Balance = Balance()
        # self.Balance.bSer = serial.Serial(self.lineEdit_4.text(), 9600, timeout=3)
        self.pushButton.clicked.connect(self.start_loop)
        self.pushButton_2.clicked.connect(self.stop_loop)

    def zero(self):
        # self.fZeroing=1
        self.ser.write("Z\r\n".encode('utf-8'))
        resp = self.ser.readline().decode()
        print(resp)
        self.textEdit.append("{}".format(resp))
        if resp[:1] == "Z" and resp[3:3] == "A":
            resp = self.ser.read(5).decode()
            print(resp)
            if resp[:1] == "Z" and resp[3:3] == 'D':
                self.textEdit.append("Success zeroing!")
            else:
                self.textEdit.append("Error zeroing!")


    def getCurrentWeight(self):
        self.ser.write("SUI\r\n".encode())
        resp = self.ser.readline().decode()
        print(resp)
        self.textEdit.append(resp)

    def start_loop(self):
        self.textEdit.append("Opening port")
        self.Balance.bSer = serial.Serial(self.lineEdit_4.text(), 19200, timeout=3)
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


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
