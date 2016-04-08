#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re

from google_api_manager import *

class MessageDataDictList(list):

    def __init__(self,keys,page_token,parent=None):
        # super(RowDataList, self).__init__(parent)
        list.__init__(self)
        print "MessageDataList init"

        self.credentials = get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

        # 添付ファイルのあるメッセージのみ抽出
        # threads = service.users().threads().list(userId="me",maxResults=10,q="from:urikake2@misumi.co.jp").execute().get("threads",[])
        print "now getting messages..."
        message_list_feed = self.service.users().messages().list(userId="me",maxResults=10,pageToken=page_token,q="from:urikake2@misumi.co.jp has:attachment subject:"+u"ミスミより請求書発行のご案内").execute()
        self.next_page_token = message_list_feed["nextPageToken"]
        messages = message_list_feed["messages"]
        for i in range( len(messages) ):
            message_data_dict = MessageDataDict( messages[i], self.service,keys )
            self.append(message_data_dict)

class MessageDataDict(dict):

    def __init__(self, message, service, keys, parent=None):
        dict.__init__(self)
        print "MessageDataDict init"

        for key in keys:
            self[key] = None

        self.__service = service
        self.id = message["id"]
        self.thread_id = message["threadId"]
        self.payload = self.__service.users().messages().get(userId="me",id=self.id).execute()["payload"]
        self.attachment_parts = filter(lambda x: x["filename"] != "", self.payload["parts"])# 添付ファイルのあるpartのみ抽出 2-4番目をとるのでもいいかも

        self.message_data_string = base64.urlsafe_b64decode(self.payload["parts"][0]["body"]["data"].encode("ASCII")).decode("utf-8")
        self.receiver = self.message_data_string.split("\n")[1][0:-3]
        self.receive_date = filter(lambda x: x["name"] == "Date", self.payload["headers"])[0]["value"]# 受信日
        self.message_id = filter(lambda x: x["name"] == "Message-ID" ,self.payload["headers"])[0]["value"]# message-id

        self.__attachments = [None,None,None]
        self.__attachment_paths = [None,None,None]

    def attachment_data(self,basename,idx):
        print("MessageDataDict.attachment_data(" + basename + " " + str(idx) + ")")
        if self.__attachments[idx] is None:
            for attachment_part in self.attachment_parts:
                if attachment_part["filename"].encode("utf-8") == basename + ".pdf":
                    self.__attachments[idx] = self.__service.users().messages().attachments().get(userId="me",messageId=self.id,id=attachment_part["body"]["attachmentId"]).execute()["data"].encode("utf-8")
                    break
        return self.__attachments[idx]

    def estimate_data(self):
        return self.attachment_data("御見積書",0)
        
    def invoice_data(self):
        return self.attachment_data("納品書",1)

    def bill_data(self):
        return self.attachment_data("御請求書",2)

    def attachment_date(self,create_func,path_func,):
        create_func()
        os.system("pdftotext -upw 160398 " + path_func())# textファイルへ変換
        file_text = open(path_func().replace(".pdf",".txt")).read()
        date_list = re.split("\D",re.findall("発行日.*\n",file_text)[0])
        while "" in date_list: date_list.remove("")
        return date_list

    def estimate_date(self):
        return self.attachment_date(self.create_estimate,self.estimate_path)

    def invoice_date(self):
        return self.attachment_date(self.create_invoice,self.invoice_path)

    def set_values(self):
        print "set_values()"
        order_data_dict = dict()
        
        self["orderdate"] = reduce(lambda x,y: x + "/" + y,self.estimate_date())# from estimate
        self["duedate"] = reduce(lambda x,y: x + "/" + y,self.invoice_date())# from invoice
        self["person"]  = self.receiver
        file_text = open(self.estimate_path().replace(".pdf",".txt")).read()
        self["price"] = re.findall("[,0-9]+\n",file_text)[4].replace("\n","")

    def attachment_path(self,idx): # path is "/tmp/<ID>御<見積書/請求書/納品書>.pdf"
        if self.__attachment_paths[idx] is None:
            self.__attachment_paths[idx] = os.path.join("/tmp", self.id + self.attachment_parts[idx]["filename"]).encode("utf-8")
        return self.__attachment_paths[idx]

    def estimate_path(self):
        return self.attachment_path(0)

    def invoice_path(self):
        return self.attachment_path(1)

    def bill_path(self):
        return self.attachment_path(2)

    def create_attachment(self,path_func,data_func):
        file_path = path_func()
        if not os.path.exists(file_path):
            print "create " + file_path

            # create pdf
            file_data = base64.urlsafe_b64decode(data_func())
            f = open(file_path, 'w')
            f.write(file_data)
            f.close()

            # convert to ppm
            basename = os.path.splitext(file_path)[0]
            os.system("pdftoppm -upw 160398 " + file_path + " " + basename)

    def create_estimate(self):
        self.create_attachment(self.estimate_path,self.estimate_data)

    def create_invoice(self):
        self.create_attachment(self.invoice_path,self.invoice_data)

    def create_bill(self):
        self.create_attachment(self.bill_path,self.bill_data)

    def print_pdf(self,pdfname):
        basename = os.path.splitext(pdfname)[0]
        os.system("lp " + basename + "*.ppm -o page-left=-20")

    def print_attachments(self):
        for create_func,path_func in [ (self.create_estimate,self.estimate_path), (self.create_invoice,self.invoice_path), (self.create_bill,self.bill_path) ]:
            create_func()
            self.print_pdf(path_func())

    def open_estimate(self):
        self.create_estimate()
        os.system("gnome-open " + os.path.splitext(self.estimate_path())[0] + "*.ppm")
