#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import base64
import re
import chardet

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from httplib2 import Http
import openpyxl

import gdata.spreadsheets.client

from logger import *
from google_api_manager import *

def convert_to_unicode(val):
    if not type(val) == unicode: val = val.decode(chardet.detect(val)['encoding'])
    return val

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

        # new
        self.table_key = u'invoicenumber'
        self.service = discovery.build('sheets', 'v4', http=self.credentials.authorize(Http()))
        self.api = self.service.spreadsheets()
        self._spreadsheet = self.api.get(spreadsheetId=self.file_id).execute()
        self._worksheets = self._spreadsheet["sheets"]
        self._sheet_dict = {}

        # # old
        # auth_token = gdata.gauth.OAuth2TokenFromCredentials(self.credentials)
        # self.spreadsheet_client = gdata.spreadsheets.client.SpreadsheetsClient()
        # auth_token.authorize(self.spreadsheet_client)

        # print "now getting sheets..."
        # self.sheets = self.spreadsheet_client.get_worksheets(self.file_id)
        # self.order_list_sheet = filter(lambda entry: entry.title.text == u'注文リスト', self.sheets.entry)[0]
        # self.selection_list_sheet = filter(lambda entry: entry.title.text == u'選択肢一覧', self.sheets.entry)[0]

        # # 一行目のデータとそのインデクスの取得
        # self.key_index_dict = {}
        # sys.stderr.write("now getting head rows...")
        # for i in range(1, 1+int(self.order_list_sheet.col_count.text)):
        #     sys.stderr.write(" " + str(i))
        #     sys.stderr.flush()
        #     cell_entry = self.spreadsheet_client.get_cell(self.file_id, self.order_list_sheet.get_worksheet_id(), 1, i)
        #     self.key_index_dict[cell_entry.cell.input_value] = reduce(lambda x,y: x+y, [v*26**i for i,v in enumerate(map(lambda x: ord(x)-ord("A")+1,re.sub("[0-9]","",cell_entry.title.text)[::-1]))])
        # print ""

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

    def get_worksheet_range(self, sheet_name):
        sheet_name = convert_to_unicode(sheet_name) # needless?
        if not self._sheet_dict.has_key(sheet_name):
            self._sheet_dict[sheet_name] = [sheet for sheet in self._worksheets if sheet['properties']['title'] == sheet_name][0]
        num_rows, num_cols = [self._sheet_dict[sheet_name]['properties']['gridProperties'][key] for key in ['rowCount','columnCount']]
        range_str = sheet_name+'!A1:'+openpyxl.Workbook().active.cell(row=num_rows,column=num_cols).coordinate
        logger.debug(sheet_name+' range: '+range_str)
        return range_str

    def get_worksheet_data(self, sheet_name):
        logger.info('get_worksheet_data()')
        range_str = self.get_worksheet_range(sheet_name)
        raw_data =  self.api.values().get(spreadsheetId=self.file_id, range=range_str).execute()['values']
        # convert to hash table
        table_data = {}
        for row in raw_data[2:]: # remove head 2 rows
            row_table = {}
            invoicenumber = u''
            for head,data in zip(raw_data[0],row):
                if head == self.table_key:
                    invoicenumber = data
                else:
                    row_table[head] = data
            table_data[invoicenumber] = row_table
        return table_data

    def set_worksheet_data(self, sheet_name, table_data):
        logger.info('set_worksheet_data()')
        sheet_name = convert_to_unicode(sheet_name)
        range_str = self.get_worksheet_range(sheet_name)
        list_data = self.api.values().get(spreadsheetId=self.file_id, range=sheet_name+'!1:2').execute()['values'] # get head 2 rows
        head_data = list_data[0]
        # convert to list data
        list_data += [[table[head] if head in table.keys() else key if head == self.table_key else u'' for head in head_data] for key,table in table_data.items()]
        self.api.values().update(spreadsheetId=self.file_id, range=range_str, body={'values':list_data}, valueInputOption='USER_ENTERED').execute()

def main():
    global spreadsheet_manager
    spreadsheet_manager = SpreadsheetManager()
    worksheet_name = u'ミスミ'
    worksheet_data = spreadsheet_manager.get_worksheet_data(worksheet_name)
    spreadsheet_manager.set_worksheet_data(worksheet_name, website_data)

if __name__ == "__main__":
    main()
