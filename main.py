#!/usr/bin/env python
import sys
import serial, serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import design  # Это наш конвертированный файл дизайна
import time
from scales import scales
from doser import doser
from PID import PID
import math
import glob

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    ser = serial

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
# Перенести на кнопку подключения!!!!!!!!!!!!
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        self.scales = scales()
        self.doser = doser()
        self.dosThread = QThread(parent=self)
        self.thread = QThread(parent=self)  # a new thread to run our background tasks in
        self.scales.moveToThread(self.thread)
        self.doser.moveToThread(self.dosThread)
        self.thread.started.connect(self.scales.updateLoop)
        self.pid = PID(P=0.5, I=0.0, D=0.201)
        self.pid.SetPoint = 100.0
        self.getDevPorts()
        # self.textEdit.append("Opening scales port")
        # self.scales.bSer = serial.Serial('/dev/ttyUSB0', 19200, timeout=3)
        # self.doser.dSer = serial.Serial('/dev/ttyUSB1', 115200, timeout=3)
        self.scales.weightReady.connect(self.updGUI)
        self.pushButton.clicked.connect(self.start_loop)
        self.pushButton_2.clicked.connect(self.stop_loop)
       # self.scales.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
       # self.scales.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
       # self.scales.finished.connect(self.scales.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
        self.dosThread.finished.connect(self.dosThread.deleteLater)
                # make sure those last two are connected to themselves or you will get random crashes
        self.thread.start()
        self.dosThread.start()

    def getDevPorts(self):
        ports=serial_ports()
        if len(ports)<=0:
            self.textEdit.append("No ports found. Check connection end restart app.")
            return -1
        for port in serial_ports():
            self.textEdit.append(port)
            if self.scales.connected == 0:
                if self.scales.connect(port):
                    self.textEdit.append("Scales connected")
                    continue
            if self.doser.connected == 0:
                if self.doser.connect(port):
                    self.textEdit.append("doser connected")
        if self.doser.connected == 0 or self.scales.connected == 0:
            self.textEdit.append("Check connection end restart app.")
            return -1

    def updGUI(self):
        self.label.setText("Working")
        self.label_11.setText(str(self.scales.curWeight))
        fill = self.scales.curWeight*100/float(self.lineEdit.text())
        self.textEdit.append(str(self.scales.isStable))
        if (fill<=96.25 and fill>=0):
            self.textEdit.append("FILL:"+str(fill)+"%")
            self.pid.update(self.scales.curWeight*100/float(self.lineEdit.text()))
            self.textEdit.append("DOSE:"+self.doser.setSpeed(math.floor(self.pid.output)))
        if (fill>96.25 and fill<103.75):
            if self.doser.speed>0:
                self.doser.setSpeed(0)
            if self.scales.isStable == True:
                self.textEdit.append("DOSING COMPLETE:")
                self.scales.working = False
        if (fill>103.75):
            if self.doser.speed>0:
                self.doser.setSpeed(0)
            if self.scales.isStable == True:
                self.textEdit.append("DOSING ERROR")
            # self.scales.working=False


    def start_loop(self):
       # self.label.setText("Zeroing")
       # for i in range(3):
       #     self.textEdit.append("Zeroing. Try("+str(i)+")")
       #     if self.scales.setZero() == 1: break
       if self.scales.connected and self.doser.connected:
            self.textEdit.append("Starting work.")
            self.scales.working = True
            self.label.setText("Working")

    def stop_loop(self):
        if self.scales.working:
            self.scales.working = False
            self.label.setText("IDLE")
            self.textEdit.append("DOSING Stoped:"+self.doser.setSpeed(0))

    def on_pushButton_6_clicked(self):
        if self.scales.working is False:
            self.label_11.setText("---.---")
            self.label.setText("Tarering")
            self.scales.tare()
        else: self.textEdit.append("Stop dosing first!!")

    def on_pushButton_5_clicked(self):
        if  self.scales.working is False:
            self.scales.update()
        else: self.textEdit.append("Stop dosing first!!")


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
