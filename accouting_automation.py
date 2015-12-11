#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re

from apiclient import errors

from menu_window import *

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    ui = GUI()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
