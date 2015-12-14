#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import gdata.spreadsheets.client

from google_api_manager import *

class SpreadsheetManager():

    def __init__(self,parent=None):
        # super(RowDataList, self).__init__(parent)
        # list.__init__(self)
        print "SpreadsheetManager init"

        self.file_id = "1QqN7rT0gv2eDrmMDnfc_FXaXhSzZhB44TVICkKaj5DA"
        
        self.credentials = get_credentials()
        # http = credentials.authorize(httplib2.Http())
        # service = discovery.build('drive', 'v2', http=http)
        # service.files().get(fileId=file_id).execute()

        auth_token = gdata.gauth.OAuth2TokenFromCredentials(self.credentials)
        self.spreadsheet_client = gdata.spreadsheets.client.SpreadsheetsClient()
        auth_token.authorize(self.spreadsheet_client)

        print "now getting sheets..."
        self.sheets = self.spreadsheet_client.get_worksheets(self.file_id)
        self.order_list_sheet = self.sheets.entry[0]
        print "now getting list feed..."
        list_feed = self.spreadsheet_client.get_list_feed( self.file_id, self.order_list_sheet.get_worksheet_id() )
        self.keys = []
        for key in list_feed.entry[0].to_dict().keys():
            self.keys.append(key)

    def send_order_data(self,message_data_dict):
        print "send_order_data()"
        print "now getting list feed"
        list_feed = self.spreadsheet_client.get_list_feed( self.file_id, self.order_list_sheet.get_worksheet_id() )

        row_idx = 1+1+len(list_feed.entry)

        print "now getting cell entry"
        cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), row_idx, 1)
        cell_entry.cell.input_value = message_data_dict["orderdate"]
        print "now updating cell entry"
        self.spreadsheet_client.update( cell_entry )

        cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), row_idx, 2)
        cell_entry.cell.input_value = message_data_dict["duedate"]
        self.spreadsheet_client.update( cell_entry )

        cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), row_idx, 5)
        cell_entry.cell.input_value = message_data_dict["price"]
        self.spreadsheet_client.update( cell_entry )

        cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), row_idx, 7)
        cell_entry.cell.input_value = message_data_dict["budget"]
        self.spreadsheet_client.update( cell_entry )

if __name__ == "__main__":
    global spreadsheet_manager
    spreadsheet_manager = SpreadsheetManager()
