# QT_learning
学习QT

1.安装Pyqt5库

pip install PyQt5

pip install pyqt5-tools

2.在pycharm添加external tools

Designer添加：

Name：工具名字，譬如QTDesigner

Program：designer.exe程序的绝对路径，在site-packages下搜索

Working directory--designer.exe工作路径，设置为  $ProjectFileDir$

PyUIC添加

name：工具名字，譬如PyUIC

Program：python.exe的绝对路径路径

Arguments：$FileName$ -o $FileNameWithoutExtension$.py

Working dirctory：$ProjectFileDir$
