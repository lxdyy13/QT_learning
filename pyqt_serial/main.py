import sys
import PyQt5.QtWidgets as qw
import serial
import threading

# 加入自己的类
from serial_thread import Serial_Qthread_function
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtGui import QTextCursor,QColor
import time

class SerialFrom(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = serial.Ui_serial()
        self.ui.setupUi(self)
        self.interface_init()
        self.UI_Init()

        print("主线程ID:", threading.currentThread().ident)

        # 加入串口线程
        self.Serial_QTread = QThread()
        self.Serial_QTread_Function = Serial_Qthread_function()
        self.Serial_QTread_Function.moveToThread(self.Serial_QTread)
        self.Serial_QTread.start()
        self.Serial_QTread_Function.signal_serialstart_function.connect(self.Serial_QTread_Function.serialinit_function)
        self.Serial_QTread_Function.signal_serialstart_function.emit()

        self.Serial_QTread_Function.signal_pushButton_Open.connect(self.Serial_QTread_Function.slot_pushButton_Open)

        self.Serial_QTread_Function.signal_pushButton_Open_flag.connect(self.slot_pushButton_Open_flag)

        self.Serial_QTread_Function.signal_ReadData.connect(self.slot_ReadData)


        self.Serial_QTread_Function.signal_DTR.connect(self.Serial_QTread_Function.slot_DTR)
        self.Serial_QTread_Function.signal_RTS.connect(self.Serial_QTread_Function.slot_RTS)

        self.Serial_QTread_Function.signal_send_data.connect(self.Serial_QTread_Function.slot_send_data)
        
        self.Serial_QTread_Function.signal_send_data_length.connect(self.signal_send_data_length)



        # 打开定时器
        self.port_name = []  # 记录扫描的串口
        self.time_scan = QTimer()
        self.time_scan.timeout.connect(self.TimeOut_Scan)
        self.time_scan.start(1000)#定时器扫描串口

        self.time_send = QTimer()
        self.time_send.timeout.connect(self.TimeOut_send)

        #初始化值
        self.receivelength=0
        self.sendlength=0

    def TimeOut_Scan(self):
        availablePort = QSerialPortInfo.availablePorts()
        new_port = []
        for port in availablePort:
            new_port.append(port.portName())  # 加入括号就不是地址

        if len(self.port_name) != len(new_port):
            self.port_name = new_port
            self.ui.comboBox_com.clear()
            self.ui.comboBox_com.addItems(self.port_name)
            # print(self.port_name)
    
    def TimeOut_send(self):
        # print("定时时间到")
        self.pushButton_send()

    def interface_init(self):  # 界面初始化
        self.baud = ('9600', '115200')
        self.stop = ('1', '1.5', '2')
        self.data = ('8', '7', '6')
        self.check = ('None', 'Odd', 'Even')

        self.ui.comboBox_baud.addItems(self.baud)
        self.ui.comboBox_stop.addItems(self.stop)
        self.ui.comboBox_data.addItems(self.data)
        self.ui.comboBox_check.addItems(self.check)

        self.ui.checkBox_rts.stateChanged.connect(self.checkBox_rts)
        self.ui.checkBox_dtr.stateChanged.connect(self.checkBox_dtr)
        # self.ui.checkBox_timeview.stateChanged.connect(self.checkBox_timeview)
        # 发送端
        self.ui.checkBox_hexsend.stateChanged.connect(self.checkBox_hexsend)
        self.ui.pushButton_send.clicked.connect(self.pushButton_send)
        #定时器
        self.ui.checkBox_timesend.stateChanged.connect(self.checkBox_timesend)
        self.ui.lineEdit_intervaltime.setText('1000')
        #清除按钮
        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear)
        self.ui.pushButton_sendclear.clicked.connect(self.pushButton_sendclear)
        

    def UI_Init(self):
        self.ui.pushButton_open.clicked.connect(self.pushButton_Open)

    def pushButton_Open(self):
        self.set_paramter={}
        self.set_paramter['comboBox_com']=self.ui.comboBox_com.currentText()
        self.set_paramter['comboBox_baud'] = self.ui.comboBox_baud.currentText()
        self.set_paramter['comboBox_stop'] = self.ui.comboBox_stop.currentText()
        self.set_paramter['comboBox_data'] = self.ui.comboBox_data.currentText()
        self.set_paramter['comboBox_check'] = self.ui.comboBox_check.currentText()
        self.Serial_QTread_Function.signal_pushButton_Open.emit(self.set_paramter)
    
    def slot_pushButton_Open_flag(self,state):
        print("串口打开状态",state)
        if state == 0:
            qw.QMessageBox.warning(self,'错误信息','串口已占用，打开失败')
        elif state==1:
            self.ui.pushButton_open.setStyleSheet("color:red")
            self.ui.pushButton_open.setText("关闭串口")
            self.time_scan.stop()
        else:
            self.ui.pushButton_open.setStyleSheet("color:black")
            self.ui.pushButton_open.setText("打开串口 ")
            self.time_scan.start(1000)#定时器扫描串口

    def slot_ReadData(self,data):
        #显示数据大小
        self.receivelength=self.receivelength+len(data)
        self.ui.label_recview.setText("接收："+ str(self.receivelength))


        # print (data)
        if self.ui.checkBox_timeview.checkState():
            time_str= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+'\r\n'
            self.ui.textEdit_receive.setTextColor(QColor(255,100,100))
            self.ui.textEdit_receive.insertPlainText(time_str)
            self.ui.textEdit_receive.setTextColor(QColor(0,0,0))

        Byte_data = bytes(data)
        if self.ui.checkBox_hexview.checkState():
            print("16进制显示")
            view_data=''
            for i in range(0,len(Byte_data)) :
                view_data=view_data +'{:02x}'.format(Byte_data[i])+' '
            self.ui.textEdit_receive.insertPlainText(view_data)
        else:
            print("字符串显示")
            print(Byte_data)
            self.ui.textEdit_receive.insertPlainText(Byte_data.decode('utf-8','ignore'))
        self.ui.textEdit_receive.moveCursor(QTextCursor.End)
            

    def checkBox_rts(self, state):
        self.Serial_QTread_Function.signal_RTS.emit(state)
        # print("rts",state)

    def checkBox_dtr(self, state):
        self.Serial_QTread_Function.signal_DTR.emit(state)
        # print("dtr",state)

    # def checkBox_timeview(self, state):
    #     print("时间戳",state)
    def checkBox_hexsend(self, state):
        print("16进制发送",state)
        if state == 2:
            send_text=self.ui.textEdit_send.toPlainText()
            Byte_text=str.encode(send_text)
            View_data=''
            for i in range(0,len(Byte_text)):
                View_data=View_data +'{:02x}'.format(Byte_text[i])+' '
            self.ui.textEdit_send.setText(View_data)
        else:
            send_list=[]
            send_text=self.ui.textEdit_send.toPlainText()
            while send_text != '':
                try:
                    num=int(send_text[0:2],16)
                except:
                     qw.QMessageBox.warning(self,'错误信息','请输入正确16进制数据')
                     return
                send_text=send_text[2:].strip()
                send_list.append(num)
            input_s=bytes(send_list)
            self.ui.textEdit_send.setText(input_s.decode())
    
    
    def pushButton_send(self):
        print ('点击发送按钮')
        send_data={}
        send_data['end']= self.ui.checkBox_end.checkState()   #发送新行
        send_data['data']=self.ui.textEdit_send.toPlainText()
        send_data['Hex']=self.ui.checkBox_hexsend.checkState()
        self.Serial_QTread_Function.signal_send_data.emit(send_data)
    
    def checkBox_timesend(self,state):
        # print ("点击定时器")
        if state==2:
            time_data=self.ui.lineEdit_intervaltime.text()
            self.time_send.start(int(time_data))
        else:
            self.time_send.stop()

    def pushButton_clear(self):#清除接收
        print("Clear")
        self.receivelength=0
        self.ui.label_recview.setText("接收:0")
        self.ui.textEdit_receive.clear()

    def pushButton_sendclear(self):#清除发送
        print("Send clear")
        self.sendlength=0
        self.ui.label_sendview.setText("发送:0")
        self.ui.textEdit_send.clear()

    def signal_send_data_length(self, length):
        self.sendlength=self.sendlength + length
        self.ui.label_sendview.setText("发送："+str(self.sendlength))
        


if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    w = SerialFrom()
    w.show()
    sys.exit(app.exec_())



















# if __name__ =="__main__":
#     app=qw.QApplication(sys.argv)
#     w=qw.QWidget()
#     ui=serial.Ui_serial()
#     ui.setupUi(w)
#     w.show()
#     sys.exit(app.exec())


# from PyQt5.QtWidgets import QWidget, QApplication

# app = QApplication(sys.argv)
# widget = QWidget()
# widget.resize(640, 480)
# widget.setWindowTitle("Hello, PyQt5!")
# widget.show()
# sys.exit(app.exec())
