#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os
import sys
import base64
import functools
 
from PySide import QtCore, QtGui

from spreadsheet_manager import *
from message import *

#------------------------------------------------------------------------------
## MainWindowを作るクラス
class MainWindow(QtGui.QWidget):
  
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.spreadsheet_manager = SpreadsheetManager()
        self.message_data_dict_list = MessageDataDictList(self.spreadsheet_manager.key_index_dict.keys())

        # 空の縦レイアウトを作る
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        # # ラジオボタン
        # self.radio = QtGui.QRadioButton('radioButton')
        # self.layout.addWidget(self.radio)

        self.check_boxes = []
        for message_data_dict in self.message_data_dict_list:
            hlayout = QtGui.QHBoxLayout()
            self.layout.addLayout(hlayout)

            # チェックボックス
            check = QtGui.QCheckBox(message_data_dict.receiver.decode("utf-8") + " " + message_data_dict.receive_date)
            hlayout.addWidget(check)
            self.check_boxes.append(check)

            # # ラインエディット
            # line_edit = QtGui.QLineEdit(row_data.receiver)
            # hlayout.addWidget(line_edit)

            # 見積書閲覧ボタン
            estimate_sheet_button = QtGui.QPushButton('View Estimate')
            estimate_sheet_button.clicked.connect( functools.partial(message_data_dict.open_estimate) )
            hlayout.addWidget(estimate_sheet_button)
            
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
                # self.order_data_input_window.closeEvent = lambda event: self.order_data_input_window_close_cb(i)
                self.order_data_input_window.send_order_data_button.clicked.connect( functools.partial(self.order_data_input_window_send_data_button_cb,i) )
                self.order_data_input_window.exec_()# wait for sub window to close

    def order_data_input_window_send_data_button_cb(self, check_box_idx):
        print "order_data_input_window_send_data_button_cb(" + str(check_box_idx) + ")"

        message_data_dict = self.message_data_dict_list[check_box_idx]
        for key,form in self.order_data_input_window.form_dict.iteritems():
            if type(form) == QtGui.QLineEdit:
                message_data_dict[key] = form.text()
            elif type(form) == QtGui.QComboBox:
                message_data_dict[key] = form.currentText()

        self.spreadsheet_manager.send_order_data(message_data_dict)
        self.order_data_input_window.close()
            
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


class ProcessAccountingWindow(QtGui.QDialog):

    def __init__(self, message_data_dict, parent=None):
        super(ProcessAccountingWindow, self).__init__(parent)

        self.message_data_dict = message_data_dict
        
        # 空の縦レイアウトを作る
        # self.layout = QtGui.QVBoxLayout()
        self.layout = QtGui.QGridLayout()
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

        self.form_dict = {}
        
        self.layout.addWidget(QtGui.QLabel("person:"),0,0)
        self.form_dict["person"] = QtGui.QLineEdit(self.message_data_dict["person"])
        self.layout.addWidget(self.form_dict["person"],0,1)

        self.layout.addWidget(QtGui.QLabel("orderdate:"),1,0)
        self.form_dict["orderdate"] = QtGui.QLineEdit(self.message_data_dict["orderdate"])
        self.layout.addWidget(self.form_dict["orderdate"],1,1)

        self.layout.addWidget(QtGui.QLabel("duedate:"),2,0)
        self.form_dict["duedate"] = QtGui.QLineEdit(self.message_data_dict["duedate"])
        self.layout.addWidget(self.form_dict["duedate"],2,1)

        self.layout.addWidget(QtGui.QLabel("price:"),3,0)
        self.form_dict["price"] = QtGui.QLineEdit(self.message_data_dict["price"])
        self.layout.addWidget(self.form_dict["price"],3,1)
        
        self.layout.addWidget(QtGui.QLabel("company:"),4,0)
        self.form_dict["company"] = QtGui.QLineEdit("株式会社 ミスミ")
        self.layout.addWidget(self.form_dict["company"],4,1)

        self.layout.addWidget(QtGui.QLabel("merchandise:"),5,0)
        self.form_dict["merchandise"] = QtGui.QLineEdit("品名")
        self.layout.addWidget(self.form_dict["merchandise"],5,1)

        # コンボボックス
        self.layout.addWidget(QtGui.QLabel("robot:"),6,0)
        self.form_dict["robot"] = QtGui.QComboBox()
        self.form_dict["robot"].addItems(["JAXON","HRP2"])
        self.layout.addWidget(self.form_dict["robot"],6,1)

        self.layout.addWidget(QtGui.QLabel("budget:"),7,0)
        self.form_dict["budget"] = QtGui.QComboBox()
        self.form_dict["budget"].addItems(['D-NEDO', 'N-NEDO', 'C'])
        self.layout.addWidget(self.form_dict["budget"],7,1)

        # Sendボタン
        self.send_order_data_button = QtGui.QPushButton('Send to Spreadsheet')
        self.layout.addWidget(self.send_order_data_button,8,0)

        # cancelボタン
        cancel_button = QtGui.QPushButton('Cancel')
        self.layout.addWidget(cancel_button,8,1)
        cancel_button.clicked.connect(self.close)

        # # スピンボックス
        # self.spin = QtGui.QSpinBox()
        # self.layout.addWidget(self.spin)
  
        # # リストウィジェット
        # self.listWidget = QtGui.QListWidget()
        # self.listWidget.addItems(['itemA', 'itemB', 'itemC'])
        # self.layout.addWidget(self.listWidget)

#------------------------------------------------------------------------------ 
## GUIの起動
def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    global ui
    ui = MainWindow()
    # ui.show()
    # sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
