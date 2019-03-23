#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, glob, copy

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from httplib2 import Http
from apiclient.http import MediaFileUpload

from logger import *
from google_api_manager import *

class DriveManager():
    def __init__(self, parent=None):
        logger.info( "DriveManager init")

        self.credentials = get_credentials()

        self.service = discovery.build('drive', 'v3', http=self.credentials.authorize(Http()))
        self.api = self.service.files()

        self.delimiter = '_'
        self._invoice_folder_dict = {}
        self._invoice_folder_dict[''] = '0B1NnnpidNMmgfnhwX25CeGJ2cllrcFNqZmhVT2Z0Q1l0YnBjcVo4djdKOThwZ3NWeUVjR0U' # 注文書

    def invoice_folder(self, target_folder_key):
        if not self._invoice_folder_dict.has_key(target_folder_key):
            parent_folder_id = self.invoice_folder(self.delimiter.join(target_folder_key.split(self.delimiter)[:-1]))
            logger.debug("parent folder : " + self.delimiter.join(target_folder_key.split(self.delimiter)[:-1]) + ',' + parent_folder_id)
            target_folder_name = target_folder_key.split(self.delimiter)[-1]
            ret = self.api.list(fields="files(id, name)",q="'"+parent_folder_id+"' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '"+target_folder_name+"'").execute().get('files')
            if len(ret) > 0:
                file_id = ret[0]['id']
            else: # create folder when no target folder
                logger.info("create " + target_folder_name)
                file_metadata = {
                    'name': target_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                    }
                file_id = self.api.create(body=file_metadata, fields='id').execute().get('id')
            logger.debug('target folder id:' + file_id)
            self._invoice_folder_dict[target_folder_key] = file_id
        return self._invoice_folder_dict[target_folder_key]

    def get_required_invoice_data(self, website_name, invoice_data):
        logger.info('get_required_invoice_data()')
        ret_data = {}
        for invoice_number,data in invoice_data.items():
            folder_name = website_name + self.delimiter + self.delimiter.join(data['duedate'].split('/')[:-1])
            parent_folder_id = self.invoice_folder(folder_name)
            ret = self.api.list(fields="files(id, name)",q="'"+parent_folder_id+"' in parents and mimeType = 'application/pdf' and trashed = false and name contains '"+invoice_number+"'").execute().get('files')
            if len(ret) < 3:
                logger.info(invoice_number+'('+data['person']+', '+data['duedate']+')'+' does not exist')
                ret_data[invoice_number] = copy.deepcopy(data)
        return ret_data

    def upload_file_and_update_invoice_data(self, website_name, invoice_data):
        logger.info('upload_invoices()')
        for invoice_number,data in invoice_data.items():
            folder_name = website_name + self.delimiter + self.delimiter.join(data['duedate'].split('/')[:-1])
            parent_folder_id = self.invoice_folder(folder_name)
            file_ids = []
            for pdf_name in data['pdf']:
                upload_name = pdf_name.split(os.path.sep)[-1]
                upload_name = re.sub('(.*)'+invoice_number+'_[0-9]*_[0-9]*.pdf', data['person']+self.delimiter+invoice_number+self.delimiter+r'\1.pdf',upload_name) # remove date numbers from file name
                file_metadata = {
                    'name': upload_name,
                    'parents': [parent_folder_id]
                    }
                media = MediaFileUpload(pdf_name, mimetype='application/pdf') # simple upload (5MB or less)
                file_ids.append('"https://drive.google.com/file/d/'+self.api.create(body=file_metadata, media_body=media, fields='id').execute().get('id')+'/edit"')
                logger.info('uploaded pdf: '+pdf_name+' as '+upload_name+'('+file_ids[-1]+')')
                os.remove(pdf_name) # remove uploaded pdf files
                logger.debug('remove pdf: '+pdf_name)
            data['driveid'] = '={'+','.join(file_ids)+'}'
