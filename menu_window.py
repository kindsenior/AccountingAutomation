#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os
import sys
import base64
 
from PySide import QtCore, QtGui

from spreadsheet_manager import *
from message import *

#------------------------------------------------------------------------------
## MainWindowを作るクラス
class MainWindow(QtGui.QWidget):
  
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.spreadsheet_manager = SpreadsheetManager()
        self.message_data_dict_list = MessageDataDictList()

        # 空の縦レイアウトを作る
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # # ラジオボタン
        # self.radio = QtGui.QRadioButton('radioButton')
        # self.layout.addWidget(self.radio)

        self.check_boxes = []
        
        for message_data in self.message_data_dict_list:
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
        self.message_data_dict_list[0].open_estimate()
        
    #----------------------------------------
    ## UI要素にシグナルを追加
    def setSignals(self):
        self.process_button.clicked.connect(self.process_accounting)

    def process_accounting(self):
        for i in range( len(self.check_boxes) ):
            if self.check_boxes[i].isChecked():
                # order_data_dict = self.message_data_dict_list[i].get_order_data()
                # print order_data_dict["orderdate"] + "price:" + order_data_dict["price"]
                self.message_data_dict_list[i].set_values()
                self.order_data_input_window = ProcessAccountingWindow( self.message_data_dict_list[i] )
                self.order_data_input_window.closeEvent = lambda event: self.order_data_input_window_close_cb(i)
                self.order_data_input_window.show()

    def order_data_input_window_close_cb(self, check_box_idx):
        print "order_data_input_window_close_cb()"

        line_edit_dict = self.order_data_input_window.line_edit_dict
        # print line_edit_dict["orderdate"].text() + " " + line_edit_dict["duedate"].text()
        message_data_dict = self.message_data_dict_list[check_box_idx]
        message_data_dict["orderdate"] = line_edit_dict["orderdate"].text()
        message_data_dict["duedate"] = line_edit_dict["duedate"].text()
        message_data_dict["price"] = line_edit_dict["price"].text()

        message_data_dict["budget"] = self.order_data_input_window.combo.currentText()

        self.spreadsheet_manager.send_order_data(message_data_dict)

            
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


class ProcessAccountingWindow(QtGui.QWidget):
  
    def __init__(self, message_data_dict, parent=None):
        super(ProcessAccountingWindow, self).__init__(parent)

        self.message_data_dict = message_data_dict
        
        # 空の縦レイアウトを作る
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # # ラジオボタン
        # self.radio = QtGui.QRadioButton('radioButton')
        # self.layout.addWidget(self.radio)

        # self.check_boxes = []
        
        # for message_data in self.message_data_dict_list:

        # # チェックボックス
        # check = QtGui.QCheckBox(message_data.receiver.decode("utf-8") + " " + message_data.receive_date)
        # self.layout.addWidget(check)
        # self.check_boxes.append(check)

        # ラインエディット

        self.line_edit_dict = {}
        
        self.line_edit_dict["orderdate"] = QtGui.QLineEdit(self.message_data_dict["orderdate"])
        self.layout.addWidget(self.line_edit_dict["orderdate"])

        self.line_edit_dict["duedate"] = QtGui.QLineEdit(self.message_data_dict["duedate"])
        self.layout.addWidget(self.line_edit_dict["duedate"])

        self.line_edit_dict["price"] = QtGui.QLineEdit(self.message_data_dict["price"])
        self.layout.addWidget(self.line_edit_dict["price"])
        
        # コンボボックス
        self.combo = QtGui.QComboBox()
        self.combo.addItems(['A', 'B', 'C'])
        self.layout.addWidget(self.combo)

        # OKボタン
        self.send_order_data_button = QtGui.QPushButton('Send to Spreadsheet')
        self.layout.addWidget(self.send_order_data_button)
        self.send_order_data_button.clicked.connect(self.close)
        # row_data.get_estimate()

        # # スピンボックス
        # self.spin = QtGui.QSpinBox()
        # self.layout.addWidget(self.spin)
  
        # # リストウィジェット
        # self.listWidget = QtGui.QListWidget()
        # self.listWidget.addItems(['itemA', 'itemB', 'itemC'])
        # self.layout.addWidget(self.listWidget)

    def update_data_and_close_window(self):
        # self.order_data_dict["orderdate"] = self.orderdate_line_edit.text()
        # self.order_data_dict["duedate"] = self.duedate_line_edit.text()
        self.close()
         
#------------------------------------------------------------------------------ 
## GUIの起動
def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
