#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os
import sys
import base64
 
from PySide import QtCore, QtGui

from spreadsheet_manager import *
from message import *

#------------------------------------------------------------------------------
## GUIを作るクラス
class GUI(QtGui.QWidget):
  
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        self.spreadsheet_manager = SpreadsheetManager()
        self.message_data_list = MessageDataList()

        # 空の縦レイアウトを作る
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # # ラジオボタン
        # self.radio = QtGui.QRadioButton('radioButton')
        # self.layout.addWidget(self.radio)

        self.check_boxes = []
        
        for message_data in self.message_data_list:
            hlayout = QtGui.QHBoxLayout()
            self.layout.addLayout(hlayout)

            # チェックボックス
            check = QtGui.QCheckBox(message_data.receiver.decode("utf-8") + " " + message_data.receive_date)
            hlayout.addWidget(check)
            self.check_boxes.append(check)

            # # ラインエディット
            # line_edit = QtGui.QLineEdit(row_data.receiver)
            # hlayout.addWidget(line_edit)

            # 最後にOKボタン
            estimate_sheet_button = QtGui.QPushButton('View Estimate')
            hlayout.addWidget(estimate_sheet_button)
            estimate_sheet_button.clicked.connect(self.open_estimate)
            
            # row_data.get_estimate()

        # # スピンボックス
        # self.spin = QtGui.QSpinBox()
        # self.layout.addWidget(self.spin)
 
        # # コンボボックス
        # self.combo = QtGui.QComboBox()
        # self.combo.addItems(['A', 'B', 'C'])
        # self.layout.addWidget(self.combo)
 
        # # リストウィジェット
        # self.listWidget = QtGui.QListWidget()
        # self.listWidget.addItems(['itemA', 'itemB', 'itemC'])
        # self.layout.addWidget(self.listWidget)
 
        # 最後にOKボタン
        self.process_button = QtGui.QPushButton('Process Accouting')
        self.layout.addWidget(self.process_button)
 
        # UI要素にシグナルを追加
        self.setSignals()

    def open_estimate(self):
        print("GUI.openPdf()")
        self.message_data_list[0].open_estimate()
        
    #----------------------------------------
    ## UI要素にシグナルを追加
    def setSignals(self):
        self.process_button.clicked.connect(self.process_accounting)

    def process_accounting(self):
        for i in range( len(self.check_boxes) ):
            if self.check_boxes[i].isChecked():
                date_list, price = self.message_data_list[i].get_order_data()
                print date_list
                print "price:" + price
                self.spreadsheet_manager.send_order_data(date_list,date_list,price)
            
    #----------------------------------------
    ## UI要素のステータスやら値やらプリントする
    def getValue(self):
        print '\n'
        print ' getValue '.center(80, '*')
        print '\n'
 
        print 'RadioButton State = ', self.radio.isChecked()
        print 'CheckBox State    = ', self.check.isChecked()
        print 'LineEdit Text     = ', self.lineEdit.text()
        print 'SpinBox Value     = ', self.spin.value()
        print 'ComboBox Index    = ', self.combo.currentIndex()
        print 'ComboBox Label    = ', self.combo.currentText()
 
        currentListIndex = self.listWidget.currentRow()
        print 'ListWidget index  = ', currentListIndex
        if currentListIndex == -1:
            print 'ListWidget Text   = None'
        else:
            print 'ListWidget Text   = ', self.listWidget.currentItem().text()
 
        print '\n'
        print ' getValue '.center(80, '*')
 
#------------------------------------------------------------------------------ 
## GUIの起動
def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    ui = GUI()
    ui.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
