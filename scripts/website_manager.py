#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, re, glob, yaml
if sys.version_info.major == 2: from io import open
import roslib
import zipfile

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions as selenium_exceptions

from logger import *

class WebsiteManager(object):
    def __init__(self, is_headless=True):
        logger.info( "WebsiteManager init")
        self.options = webdriver.ChromeOptions()

        if is_headless: self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.package_dir = roslib.packages.get_pkg_dir('accounting_automation')
        self.download_dir = os.path.join(self.package_dir, 'downloads')
        # self.options.add_argument('download.default_directory='+self.download_dir) # do not work
        prefs = {"download.default_directory" : self.download_dir}
        self.options.add_experimental_option("prefs", prefs)
        self.is_headless = is_headless

        self.driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", chrome_options=self.options) # only Linux

    def get_and_save_user_data(self, read_from_stdin=False):
        login_data_file_name = os.path.join(self.package_dir, 'login_data_file.yaml')

        # open or create file and create data instance
        try:
            login_data_file = open(login_data_file_name, 'r+', encoding=sys.getfilesystemencoding())
            login_data = yaml.load(login_data_file) # file pointer moves to end
            if login_data is None: raise(IOError)
            logger.info('opened and read '+login_data_file_name)
            logger.debug('yaml data(read):' + str(login_data))
        except IOError:
            login_data_file = open(login_data_file_name, 'w')
            login_data = {}
            logger.info('created '+login_data_file_name)

        # read or type in data, set data to instance and save as file
        try:
            if read_from_stdin: raise(KeyError)
            username = login_data[self.worksheet_name]['username']
            password = login_data[self.worksheet_name]['password']
        except KeyError:
            login_data[self.worksheet_name] = {}
            username = login_data[self.worksheet_name]['username'] = raw_input('username: ')
            password = login_data[self.worksheet_name]['password'] = raw_input('password: ')
            logger.debug('yaml data(write):' + str(login_data))
            login_data_file.seek(0) # move file pointer to head
            yaml.safe_dump(login_data, login_data_file, encoding=sys.getfilesystemencoding(), allow_unicode=True) # use safe_dump and allow_unicode=True for unicode

        # close file
        login_data_file.close()

        return username, password

    def username_box(self): return self.driver.find_element(self.username_type, self.username_key)

    def password_box(self): return self.driver.find_element(self.password_type, self.password_key)

    def login_button(self): return self.driver.find_element(self.login_button_type, self.login_button_key)

    def is_logined(self):
        try:
            self.driver.find_element_by_class_name('lc-user')
            return True
        except selenium_exceptions.NoSuchElementException:
            logger.critical('Failed login. Please check username and password')
            return False

    def login(self, read_from_stdin=False):
        self.go_to_login_page()

        username, password = self.get_and_save_user_data(read_from_stdin)
        logger.critical('login by username: '+username+' password: '+password)
        username_box = self.username_box()
        password_box = self.password_box()
        username_box.clear()
        password_box.clear()
        username_box.send_keys(username)
        password_box.send_keys(password)
        self.login_button().click()
        if not self.is_logined(): super(MisumiManager, self).login(True)

    def go_to_login_page(self):
        self.driver.get(self.login_url)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((self.login_button_type, self.login_button_key))) # wait for opening window

    def go_to_invoice_page(self, do_update=False):
        if do_update or not self.invoice_page_handle in self.driver.window_handles:
            self.driver.get(self.invoice_url)
            self.invoice_page_handle = self.driver.current_window_handle
        else:
            self.driver.switch_to_window(self.invoice_page_handle) # only switch windows

class MisumiManager(WebsiteManager):
    def __init__(self, is_headless=True):
        logger.info( "MisumiManager init")
        super(MisumiManager, self).__init__(is_headless)
        self.worksheet_name = u'ミスミ'
        self.invoice_url = 'https://ec.misumi.jp/wos/common/EC003WosTopCmd.do?commandCode=INVOICE_LIST'

    def login(self):
        logger.info('login()')
        self.login_url = 'https://ec.misumi.jp/wos/common/EC002SingleLoginCmd.do'
        # user name: <input type="text" class="id requiredArea inputsize_30 fsL_inputTag imeOff" name="loginId" maxlength="50" value="jsk00">
        self.username_type = By.NAME; self.username_key = 'loginId'
        # pass: <input type="password" class="pass requiredArea inputsize_30 fsL_inputTag" name="password" maxlength="15" value="" onkeypress="key_On(window.event.keyCode)">
        self.password_type = By.NAME; self.password_key = 'password'
        # download button: <input id="loginCommand" type="submit" class="btn" onclick="doLogin();">
        self.login_button_type = By.ID; self.login_button_key = "loginCommand"

        super(MisumiManager, self).login()

    def publish_unpublished_invoices(self):
        target_url = 'https://ec.misumi.jp/wos/common/EC003WosTopCmd.do?commandCode=INVOICE_STDCUSTOM_PDF'
        self.driver.get(target_url)
        try:
            table = self.driver.find_element_by_class_name("marginTableTB")
            # check box
            check_boxes = table.find_elements_by_id("chkInvoice")
            [check_box.click() for check_box in check_boxes]

            # publish button
            publish_without_change_button = self.driver.find_element_by_id("buttonWithoutChange")
            publish_without_change_button.click()

            publish_confirmation_button = self.driver.find_element_by_class_name("btnPublish")
            publish_confirmation_button.click()
            logger.info("Published new invoices")
        except selenium_exceptions.NoSuchElementException:
            logger.info("No unpublished invoices")

    def update_invoice_data(self):
        logger.info('update_invoice_data()')
        # unpublished invoices
        self.publish_unpublished_invoices()

        # published invoices
        # get table
        self.go_to_invoice_page(do_update=True)
        self.invoice_table = self.driver.find_element_by_xpath('//*[@class="marginTableTB invoiceTable"]')

        # parse data
        # head_row = [[cel.text for cel in row.find_elements_by_tag_name("th")] for row in self.invoice_table.find_elements_by_tag_name("tr")][0]
        content_rows = [[cel.text for cel in row.find_elements_by_tag_name("td") if len(cel.text) > 0 ] for row in self.invoice_table.find_elements_by_tag_name("tr")][1:] # remove first empty column
        logger.debug("content_rows:")
        logger.debug(content_rows)

        check_boxes = self.invoice_table.find_elements_by_id("chkInvoice")
        self._invoice_dict = {}
        self._check_box_dict = {}
        for row,check_box in zip(content_rows, check_boxes):
            invoice_number = row[0].split('\n')[1].split(' ')[1]
            self._invoice_dict[invoice_number] = {u'orderdate':row[2].split('\n')[-2], u'duedate':row[2].split('\n')[-1], u'price':row[3]} # set invoice data except person
            self._check_box_dict[invoice_number] = check_box # get check boxes

        # set person from invoice links
        invoice_links = self.invoice_table.find_elements_by_id("QuotationInvoice")
        for invoice_link in invoice_links:
            invoice_link.click()
            logger.debug("window_handles:" + self.driver.window_handles[-1])
            self.driver.switch_to_window(self.driver.window_handles[-1])
            table_key = "marginTableTB"
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, table_key))) # wait for switching window
            sub_table = self.driver.find_element_by_class_name(table_key)
            detail = [cel.text for row in sub_table.find_elements_by_tag_name("tr") for cel in row.find_elements_by_tag_name("td")]
            logger.debug(str(detail).decode("unicode-escape"))
            self._invoice_dict[re.findall('[A-z]+[0-9]+',detail[0].split('\n')[1])[0]][u'person'] = detail[2].split('\n')[-1]
            self.driver.close()
            self.go_to_invoice_page(do_update=False)

    def get_invoice_data(self):
        logger.info('get_invoice_data()')
        # self.update_invoice_data()
        return self._invoice_dict

    def download_and_set_invoice_data(self, required_invoice_data):
        logger.info('download_and_set_invoice_data()')
        self.go_to_invoice_page(do_update=False)

        if len(required_invoice_data) > 0:
            # download invoices
            download_button = self.driver.find_element_by_class_name("btnDownload")
            for invoice_number, check_box in self._check_box_dict.items():
                if invoice_number in required_invoice_data.keys():
                    check_box.click()
            download_button.click()
            time.sleep(3)
            self.driver.switch_to_alert().accept() # alert
            # sometimes fail in downloading

            # extract zip
            while True:
                logger.critical('waiting for downloading invoice zip file.....')
                zip_files = glob.glob(os.path.join(self.download_dir,'*.zip'))
                time.sleep(5)
                if len(zip_files) > 0:
                    for zip_file in zip_files:
                        logger.debug('found zip:'+zip_file)
                        zipfile.ZipFile(zip_file,'r').extractall(self.download_dir) # extract zip
                        logger.debug('remove zip: '+zip_file)
                        os.remove(zip_files[0]) # remove zip
                    break

            # set pdf file names
            [invoice_datum.update(pdf=glob.glob(os.path.join(self.download_dir,'*'+invoice_number+'*.pdf'))) for invoice_number,invoice_datum in required_invoice_data.items()] # overwrite variable
        else:
            logger.info('No invoce is required')

def main():
    global website_manager
    website_manager = MisumiManager()
    website_manager.login()
    website_manager.update_invoice_data()
    website_data = website_manager.get_invoice_data()

if __name__ == "__main__":
    main()
