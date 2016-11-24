#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
import random

import requests
import json
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
import bs4
import re
import argparse
reload(sys)
sys.setdefaultencoding("utf-8")




class wait_for_text_to_match(object):
    def __init__(self, locator, pattern):
        self.locator = locator
        self.pattern = re.compile(pattern)

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).get_attribute('value')
            return self.pattern.search(element_text)
        except StaleElementReferenceException:
            return False




class JDLogin(object):
	def __init__(self,user_name,user_password):
		self.session=requests.Session()

		self.browser = webdriver.PhantomJS()
		self.pubKey=''
		self.user_name=user_name
		self.user_password=user_password
		self.login_success=False


	def get_login_data(self):
		self.browser.get("https://passport.jd.com/new/login.aspx")
		
		try:
			WebDriverWait(self.browser, 10).until(wait_for_text_to_match((By.ID, "eid"), r"^\s*\S.*"))
			print "Page is ready!"
			
		except TimeoutException:
			print "Loading took too much time!"
			

		#处理cookie
		cookies=self.browser.get_cookies()
		for cookie in cookies:
			#self.session.cookies.set(cookie['name'], cookie['value'],domain=cookie['domain'],expires=cookie['expiry'],path=cookie['path'],secure=cookie['secure'])
			self.session.cookies.set(cookie['name'], cookie['value'],domain=cookie['domain'])
		#print self.session.cookies

		soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")
		hide_fields = soup.select('#formlogin input[type=hidden]')

		hide_len = len(hide_fields)
		for i in range(hide_len - 1):
			name = hide_fields[i]['name']
			value = hide_fields[i]['value']
			if name == 'uuid':
				uuid = value
			elif name == 'eid':
				eid = value
			elif name == 'fp':
				fp = value
			elif name == '_t':
				_t = value
			elif name == 'loginType':
				loginType = value
			elif name=='pubKey':
				self.pubKey=value
		last_field_name = hide_fields[-1]['name']
		last_field_value = hide_fields[-1]['value']
		#print  uuid, eid, fp, _t, loginType, last_field_name, last_field_value
		#encrypted_password=jdlogin.browser.execute_script("var encrypt = new JSEncrypt();encrypt.setPublicKey('%s');return encrypt.encrypt('%s');" % (self.pubKey,self.user_password))
		#这里使用原密码和加密过后的密码都是可以成功登录的
		encrypted_password=self.user_password
		postparam = {"uuid": uuid, "eid": eid, "fp": fp, "_t": _t, "loginType": loginType, "loginname": self.user_name,
					 "nloginpwd": encrypted_password, "chkRememberMe": 'on', "authcode": ''}
		return  postparam
	def do_login_post(self,post_data):
		query_string = {
			'r': random.random(),
			'uuid': post_data['uuid'],
			'version': 2015,
		}

		response = self.session.post('https://passport.jd.com/uc/loginService', data=post_data, params=query_string)
		if self.is_response_status_ok(response):
			ret_json = json.loads(response.text[1:-1])
			print ret_json

			if  ret_json.get('success'):
				self.login_success=True
				return True

			else:
				return False

		return False

	def is_response_status_ok(self,response):
		if response.status_code != 200:
			return False
		return True
	def login(self):
		post_data=self.get_login_data();
		ret=self.do_login_post(post_data)
		return  ret

	def get_logined_cookies(self):
		if self.login_success==True:
			return  self.session.cookies
		return  False
	def is_logined(self):
		response=self.session.get('http://i.jd.com/user/info',allow_redirects=False)
		return not  response.is_redirect
	def get_logined_cookies(self):
		if self.is_logined():
			return self.session.cookies
		return  False

parser = argparse.ArgumentParser(description='模拟京东登录')
parser.add_argument('-u','--username')
parser.add_argument('-p','--password')
options = parser.parse_args()
print options

jdlogin=JDLogin(options.username,options.password)
print jdlogin.login()
print jdlogin.get_logined_cookies()
