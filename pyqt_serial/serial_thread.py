import sys
# from PyQt5.QtWidgets import QWidget, QApplication
# from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtCore import *

import PyQt5.QtWidgets as qw
from time import sleep
import threading

from PyQt5.QtSerialPort import QSerialPort


class Serial_Qthread_function(QObject):
    signal_serialstart_function = pyqtSignal()
    signal_pushButton_Open = pyqtSignal(object)
    signal_pushButton_Open_flag = pyqtSignal(object)
    signal_ReadData = pyqtSignal(object)

    signal_DTR = pyqtSignal(object)
    signal_RTS = pyqtSignal(object)


    signal_send_data = pyqtSignal(object)
    #接收显示长度
    signal_send_data_length = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Serial_Qthread_function, self).__init__(parent)
        print("初始化时候线程", threading.currentThread().ident)
        self.state = 0 #0 未打开 1 打开 2占用/错误
        # 开始调用网络的信号

    def slot_DTR(self,state):
        print("Slot DTR",state)
        if state == 2:
            self.Serial.setDataTerminalReady(True)
        else:
            self.Serial.setDataTerminalReady(False)

    def slot_RTS(self,state):
        print("Slot RTR",state)
        if state == 2:
            self.Serial.setRequestToSend(True)
        else:
            self.Serial.setRequestToSend(False)

    def slot_pushButton_Open(self, parameter):
        if self.state == 0:
            print(parameter)
            self.Serial.setPortName(parameter['comboBox_com'])
            self.Serial.setBaudRate(int(parameter['comboBox_baud']))

            if parameter['comboBox_stop']=='1.5':
                self.Serial.setStopBits(3)
            else:
                self.Serial.setStopBits(int(parameter['comboBox_stop']))
            
            self.Serial.setDataBits(int(parameter['comboBox_data']))

            setparity1=0
            
            if parameter['comboBox_check']=='None':
                setparity1=0
            elif parameter['comboBox_check']=='Odd':
                setparity1=3
            else:
                setparity1=2
            
            self.Serial.setParity(setparity1)

            if self.Serial.open(QSerialPort.ReadWrite)==True:
                print("打开串口成功")
                self.state=1
                self.signal_pushButton_Open_flag.emit(self.state)
            else:
                print("打开串口失败")
                self.signal_pushButton_Open_flag.emit(0)
        else:
            self.state=0
            self.Serial.close()
            print("串口已关闭")
            self.signal_pushButton_Open_flag.emit(2)


    def slot_send_data(self, send_data):
        if self.state !=1:
            return
        print("发送数据",send_data['Hex'],send_data['data'])
        send_buff=''
        if send_data['Hex'] == 2:
            send_list=[]
            send_text=send_data['data']
            while send_text != '':
                try:
                    num=int(send_text[0:2],16)
                except:
                        return
                send_text=send_text[2:].strip()
                send_list.append(num)
            input_s=bytes(send_list).decode()
            if send_data['end']==2:
                send_buff=input_s+'\r\n'
            else:
                send_buff=input_s
        else:
            # Byte_data=str.encode(send_data['data'])
            if send_data['end']==2:
                send_buff=send_data['data']+'\r\n'
            else:
                send_buff=send_data['data']

        Byte_data=str.encode(send_buff)     
        self.Serial.write(Byte_data)
        #发送成功
        self.signal_send_data_length.emit(len(Byte_data))





    def Serial_receive_data(self):  # 接收串口回调函数
        print("接收数据线程id:", threading.currentThread().ident)
        # print(self.Serial.readAll())
        self.signal_ReadData.emit(self.Serial.readAll())

    def serialinit_function(self):
        print("串口线程ID:", threading.current_thread().ident)
        self.Serial = QSerialPort()
        # self.Serial.readyRead.connect(self.Serial_receive_data)
        self.Serial.readyRead.connect(self.Serial_receive_data)


















# class InitForm(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.ui = ui_test.Ui_Form()
#         self.ui.setupUi(self)
#         self.setWindowTitle("测试")
#
#         print("主线程id:", threading.current_thread().ident)
#
#         self.test1_QThread = QThread()
#         self.test1_Qthread_function = test_Qthread_function()
#         self.test1_Qthread_function.moveToThread(self.test1_QThread)
#         self.test1_QThread.start()
#
#         self.test1_Qthread_function.signal_start_function.connect(self.test1_Qthread_function.qthread_function1)
#         self.test1_Qthread_function.signal_start_function.emit()  # 运行第一次
#         self.test1_Qthread_function.signal_start_function.emit()  # 运行第二次
#
#     def closeEvent(self, event):
#         print("窗体关闭")
#         self.test1_QThread.quit()  # 回收线程
#         self.test1_QThread.wait()  # 回收线程
#         del self.test1_Qthread_function
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w1 = InitForm()
#     w1.show()
#     sys.exit(app.exec_())
