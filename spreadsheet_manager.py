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
        # print "now getting list feed..."
        # list_feed = self.spreadsheet_client.get_list_feed( self.file_id, self.order_list_sheet.get_worksheet_id() )

        # 一行目のデータとそのインデクスの取得
        self.key_index_dict = {}
        sys.stderr.write("now getting head rows...")
        for i in range(1, 1+int(self.order_list_sheet.col_count.text)):
            sys.stderr.write(" " + str(i))
            sys.stderr.flush()
            cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), 1, i)
            self.key_index_dict[cell_entry.cell.input_value] = reduce(lambda x,y: x+y, [v*26**i for i,v in enumerate(map(lambda x: ord(x)-ord("A")+1,re.sub("[0-9]","",cell_entry.title.text)[::-1]))])
        print ""

    def send_order_data(self,message_data_dict):
        print "send_order_data()"
        print "now getting list feed"
        list_feed = self.spreadsheet_client.get_list_feed( self.file_id, self.order_list_sheet.get_worksheet_id() )

        row_idx = 1+1+len(list_feed.entry)

        for key,value in message_data_dict.iteritems():
            print "now getting cell entry"
            cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), row_idx, self.key_index_dict[key])
            cell_entry.cell.input_value = value
            print "now updating :" + key
            self.spreadsheet_client.update( cell_entry )

if __name__ == "__main__":
    global spreadsheet_manager
    spreadsheet_manager = SpreadsheetManager()
