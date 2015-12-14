#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re

from google_api_manager import *

class MessageDataDictList(list):

    def __init__(self,keys,parent=None):
        # super(RowDataList, self).__init__(parent)
        list.__init__(self)
        print "MessageDataList init"

        self.credentials = get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

        # 添付ファイルのあるメッセージのみ抽出
        # threads = service.users().threads().list(userId="me",maxResults=10,q="from:urikake2@misumi.co.jp").execute().get("threads",[])
        print "now getting messages..."
        messages = self.service.users().messages().list(userId="me",maxResults=10,q="from:urikake2@misumi.co.jp has:attachment").execute()["messages"]
        for i in range( len(messages) ):
            message_data_dict = MessageDataDict( messages[i], self.service,keys )
            self.append(message_data_dict)

class MessageDataDict(dict):

    def __init__(self, message, service, keys, parent=None):
        dict.__init__(self)
        print "MessageDataDict init"

        for key in keys:
        # for key in ["orderdate","duedate","price"]:
            self[key] = None

        self.__service = service
        self.id = message["id"]
        self.payload = self.__service.users().messages().get(userId="me",id=self.id).execute()["payload"]
        self.attachment_parts = filter(lambda x: x["filename"] != "", self.payload["parts"])# 添付ファイルのあるpartのみ抽出 2-4番目をとるのでもいいかも

        self.receiver = base64.urlsafe_b64decode(self.payload["parts"][0]["body"]["data"].encode("ASCII")).split("\n")[1][0:-4]
        self.receive_date = filter(lambda x: x["name"] == "Date", self.payload["headers"])[0]["value"]# 受信日

        self.__attachments = [None,None,None]
        self.__attachment_paths = [None,None,None]

    def attachment_data(self,basename,idx):
        print("MessageData.attachment_data(" + basename + " " + str(idx) + ")")
        if self.__attachments[idx] is None:
            for attachment_part in self.attachment_parts:
                if attachment_part["filename"].encode("utf-8") == basename + ".pdf":
                    return self.__service.users().messages().attachments().get(userId="me",messageId=self.id,id=attachment_part["body"]["attachmentId"]).execute()["data"]
            return false
        return self.__attachments[idx]

    def estimate_data(self):
        return self.attachment_data("御見積書",0)
        
    def invoice_data(self):
        return self.attachment_data("納品書",2)

    def bill_data(self):
        return self.attachment_data("御請求書",1)

    def attachment_date(self,create_func,path_func,):
        create_func()
        os.system("pdftotext -upw 160398 " + path_func().encode("utf-8"))# textファイルへ変換
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

    def attachment_path(self,idx):
        if self.__attachment_paths[idx] is None:
            self.__attachment_paths[idx] = os.path.join("/tmp", self.id + self.attachment_parts[idx]["filename"])
        return self.__attachment_paths[idx]

    def estimate_path(self):
        return self.attachment_path(0)

    def invoice_path(self):
        return self.attachment_path(2)

    def create_attachment(self,path_func,data_func):
        if not os.path.exists(path_func()):
            file_data = base64.urlsafe_b64decode(data_func().encode('UTF-8'))
            f = open(path_func(), 'w')
            f.write(file_data)
            f.close()

    def create_estimate(self):
        self.create_attachment(self.estimate_path,self.estimate_data)

    def create_invoice(self):
        self.create_attachment(self.invoice_path,self.invoice_data)

    def open_estimate(self):
        estimate_path = self.estimate_path()
        self.create_estimate()
        os.system("gnome-open " + estimate_path.encode("utf-8"))

