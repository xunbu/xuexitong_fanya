from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore,QtGui
from PySide6.QtWidgets import QApplication,QWidget
from fanya import shuake ,shuakesignal
from threading import Thread,RLock
from UI import Ui_Form
from globalvalues import globaldict
from PySide6.QtWidgets import QTableWidget,QTableWidgetItem


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.chooseindexlist=[]
        self.index_total=[]
        self.ui=Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.start)
        globaldict['urllock'].acquire()#这样子lock都变为大小为0的同步信号量啦
        globaldict['messagelock'].acquire()

        shuakesignal.sendindexsignal.connect(self.displaytable)
        shuakesignal.sendprintsignal.connect(self.displaytext)

        runshuake()
    def start(self):
        globaldict['lessonurl']=self.ui.lineEdit.text()
        globaldict['urllock'].release()

    def displaytable(self,indexlist):
        for i in indexlist:
            self.index_total.append(i[0])
        print('index_total',self.index_total)
        table=self.ui.tableWidget
        table.setRowCount(len(indexlist))
        for i,value in enumerate(indexlist):
            index, title=value
            checkeditem=QTableWidgetItem()
            checkeditem.setText('')
            # stateitem= QTableWidgetItem()
            # stateitem.setText('未完成')
            titleitem=QTableWidgetItem()
            titleitem.setText(title)
            table.setItem(i,0,checkeditem)
            # table.setItem(i,1,stateitem)
            table.setItem(i,1,titleitem)
        table.cellClicked.connect(self.chooseindex)
        self.ui.pushButton_3.clicked.connect(self.chooseall)
        self.ui.pushButton_4.clicked.connect(self.choosenone)
        self.ui.pushButton_2.clicked.connect(self.sendindex)

    def chooseall(self):
        table=self.ui.tableWidget
        for i in range(0,table.rowCount()):
            table.item(i,0).setText('√')
        self.chooseindexlist=list(range(0,table.rowCount()))

    def choosenone(self):
        table=self.ui.tableWidget
        for i in range(0,table.rowCount()):
            table.item(i,0).setText('')
        self.chooseindexlist=[]

    def chooseindex(self,row,col):
        table = self.ui.tableWidget
        if col!=0:
            pass
        else:
            if table.item(row,0).text()=='':
                table.item(row,0).setText('√')
                self.chooseindexlist.append(row)
            else:
                table.item(row,0).setText('')
                self.chooseindexlist.pop(self.chooseindexlist.index(row))

    def displaytext(self,str):
        self.ui.plainTextEdit.appendPlainText(str)

    def sendindex(self):
        l_temp=[]
        for idx,i in enumerate(self.index_total):
            if idx in self.chooseindexlist:
                l_temp.append(i)
        l_temp.sort()
        globaldict['message']=l_temp
        globaldict['messagelock'].release()

def runshuake():
    thread=Thread(target=shuake)
    thread.setDaemon(True)
    thread.start()

app = QApplication([])
mainw = MainWindow()
mainw.show()
app.exec()
