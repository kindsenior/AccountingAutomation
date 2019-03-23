#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re

from apiclient import errors

from menu_window import *
import spreadsheet_manager as ssm
import drive_manager as dm
import website_manager as wm

def old_main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )# for japanese
    global ui
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())

def main():
    global spreadsheet_manager
    spreadsheet_manager = ssm.SpreadsheetManager()
    global drive_manager
    drive_manager = dm.DriveManager()
    global website_manager
    # website_manager = wm.MisumiManager(is_headless=False)
    website_manager = wm.MisumiManager(is_headless=True)

    website_manager.login()

    # update invoice data
    website_manager.update_invoice_data()
    global website_data
    website_data = website_manager.get_invoice_data()

    global worksheet_data
    worksheet_data = spreadsheet_manager.get_worksheet_data(website_manager.worksheet_name)
    website_data.update(worksheet_data) # integrate website and worksheet data (overwrite website data by worksheet data)

    # download and upload invoice pdf
    global required_invoice_data
    required_invoice_data = drive_manager.get_required_invoice_data(website_manager.worksheet_name, website_data)
    website_manager.download_and_set_invoice_data(required_invoice_data)
    drive_manager.upload_file_and_update_invoice_data(website_manager.worksheet_name, required_invoice_data) # add pdf url to data

    website_data.update(required_invoice_data) # integrate website and local data (overwrite website data by local data)
    spreadsheet_manager.set_worksheet_data(website_manager.worksheet_name, website_data)

if __name__ == '__main__':
    main()
