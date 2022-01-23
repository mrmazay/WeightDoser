#!/usr/bin/env python
import sys, serial, serial.tools.list_ports, warnings
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QThread, pyqtSlot
import design  # Это наш конвертированный файл дизайна
import time

# port tespit etme - baslangic
ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'USB' in p.description
]

# if not ports:
#    raise IOError("Seri Baglantili cihaz yok!")

if len(ports) > 1:
    warnings.warn('Baglanildi....')


class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(str)
    ser = serial
    fZeroing = 0
    fZero = 0
    fStabeling = 0
    fStable = 0
    fGetWeight = 0
    @pyqtSlot()
    def __init__(self):
        super(Worker, self).__init__()
        self.working = True

    def work(self):
        while self.working:
            line = self.ser.read_until().decode()
            print(line)
            time.sleep(0.1)
          #  response = line.split()
            self.intReady.emit(line)
            # if line != '':
            # self.textEdit_3.append(line)

        self.finished.emit()
    def zero(self):
        self.fZeroing=1
        self.ser.write("Z\r\n".encode('utf-8'))

    def getCurrentWeight(self):
        self.ser.write("SUI\r\n".encode())

class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton.clicked.connect(self.start_loop)
        self.pushButton_2.clicked.connect(self.stop_loop)
        

    def loop_finished(self):
                print('Looped Finished')

    def start_loop(self):
        self.worker = Worker()  # a new worker to perform those tasks
        self.worker.ser=serial.Serial(self.lineEdit_4.text(), 9600)
        self.thread = QThread()  # a new thread to run our background tasks in
        self.worker.moveToThread(self.thread)  # move the worker into the thread, do this first before connecting the signals
        self.thread.started.connect(self.worker.work)
                # begin our worker object's loop when the thread starts running
        self.worker.intReady.connect(self.onIntReady)

        self.pushButton_2.clicked.connect(self.stop_loop)  # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
                # make sure those last two are connected to themselves or you will get random crashes
        self.thread.start()

    def stop_loop(self):
                self.worker.working = False
                self.worker.ser.close()

    def onIntReady(self, i):
                self.textEdit.append("{}".format(i))
                arr = i.split()
                self.label_11.setText(arr[1]+' '+arr[2])
                # print(arr[0])

    def on_pushButton_6_clicked(self):
        self.worker.zero()

    def on_pushButton_5_clicked(self):
        self.worker.getCurrentWeight()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
