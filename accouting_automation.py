#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re

from apiclient import errors

from menu_window import *

def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
