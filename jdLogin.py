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
import os.path
reload(sys)
sys.setdefaultencoding("utf-8")

def saveDictToFile(Dictp,filename):
	with open(filename,'w') as data_json:
		json.dump(Dictp,data_json)

def readDictFromFile(filename):
	with open(filename) as json_data_file:
		try:
			data = json.load(json_data_file)
		except:
			return dict()
	return data





def saveCookieJarToFile(cookieJar,filename):
	saveDictToFile(requests.utils.dict_from_cookiejar(cookieJar),filename)


def readCookieJarFromFile(filename):
	return requests.utils.cookiejar_from_dict(readDictFromFile(filename))


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
		self.status_is_logined=False
		self.uuid=''
		self.login_page="https://passport.jd.com/new/login.aspx"
		self.session.headers.update({
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
			'Referer':self.login_page
		})
		self.reload_cookies()


	def get_login_data(self):
		self.browser.get(self.login_page)
		
		try:
			WebDriverWait(self.browser, 10).until(wait_for_text_to_match((By.ID, "eid"), r"^\s*\S.*"))
			print "Page is ready!"
			
		except TimeoutException:
			print "Loading took too much time!"
			return False
			

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
				self.uuid = value
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
		authcode=''
		if self.check_if_auth_code(self.user_name):
			authcode = self.download_auth_code(self.uuid)
		else:
			print u'不需要验证码登录'
		postparam = {"uuid": self.uuid, "eid": eid, "fp": fp, "_t": _t, "loginType": loginType, "loginname": self.user_name,
					 "nloginpwd": encrypted_password, "chkRememberMe": 'on', "authcode": authcode}
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
				self.status_is_logined=True
				self.save_cookies()
				return True

			else:
				return False

		return False

	def check_if_auth_code(self, usr_name):
		post_data = {'loginName': usr_name}
		query_string = {'r': random.random(),'version': 2015}
		response = self.session.post("https://passport.jd.com/uc/showAuthCode", data=post_data, params=query_string)
		if self.is_response_status_ok(response):
			js = json.loads(response.text[1:-1])
			return js['verifycode']
		print u'检查是否需要验证码API调用失败'
		return False

	def download_auth_code(self, uuid):
		#下载验证码的时候不加Referer头永远提示验证码错误

		image_file_path = os.path.join(os.getcwd(), '%s-yanzhengma.jpg'%(self.user_name))

		query_string = {
			'a': 1,
			'acid': uuid,
			'uid': uuid,
			'yys': str(int(round(time.time() * 1000))),
		}
		response = self.session.get("https://authcode.jd.com/verify/image", params=query_string)
		if not self.is_response_status_ok(response):
			print u'下载验证码失败'
			return False
		with open(image_file_path, 'wb') as f:
			for chunk in response.iter_content(chunk_size=1024):
				f.write(chunk)

		os.system('open ' + image_file_path)
		return str(raw_input('请输入验证码:'))

	def is_response_status_ok(self,response):
		if response.status_code != 200:
			return False
		return True

	def login(self):
		post_data=self.get_login_data();
		if post_data==False:
			return  False
		ret=self.do_login_post(post_data)
		return  ret

	def is_logined(self):
		response=self.session.head('http://i.jd.com/user/info',allow_redirects=False)
		status= not  response.is_redirect
		if status ==True :
			#现在在登录状态
			self.status_is_logined=True
		else:
			self.status_is_logined = False
		return  status


	def get_logined_cookies(self):
		if self.is_logined():
			return self.session.cookies
		else:
			print u'重新登录'
			if self.login()==True:
				return self.session.cookies
			return False

	def save_cookies(self):
		saveCookieJarToFile(self.session.cookies,"%s.cookie.json"%(self.user_name))

	def reload_cookies(self):
		cookiejar=None
		file_name="%s.cookie.json"%(self.user_name)
		if os.path.isfile(file_name):
			cookiejar=readCookieJarFromFile(file_name)
			self.session.cookies=cookiejar
		if cookiejar != None:
			self.session.cookies=cookiejar
			print u'从文件读入cookie'


parser = argparse.ArgumentParser(description='模拟京东登录')
parser.add_argument('-u','--username')
parser.add_argument('-p','--password')
options = parser.parse_args()

jdlogin=JDLogin(options.username,options.password)
print jdlogin.get_logined_cookies()


