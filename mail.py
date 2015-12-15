#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import mimetypes
import os

def create_body(message,subject,sender,receiver,in_reply_to=None,thread_id=None,encoding='iso-2020-jp'):
    mime_text = MIMEText(message.encode(encoding),'plain',encoding)
    mime_text["subject"] = Header(subject.encode(encoding),encoding)
    mime_text["from"] = sender
    mime_text["to"] = receiver
    if in_reply_to != None: mime_text["In-Reply-To"] = in_reply_to
    mime_dict = {'raw': base64.urlsafe_b64encode(mime_text.as_string())}
    if thread_id != None: mime_dict['threadId'] = str(thread_id)
    return mime_dict
