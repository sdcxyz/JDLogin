#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
import requests
import json
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import bs4
reload(sys)
sys.setdefaultencoding("utf-8")




class JDLogin(object):
	def __init__(self):
		self.session=requests.Session()

		self.browser = webdriver.PhantomJS()
		self.f1=''


	def get_login_data(self):
		self.browser.get("https://passport.jd.com/new/login.aspx")
		#处理cookie
		cookies=self.browser.get_cookies()
		try:
			WebDriverWait(browser, delay).until(EC.presence_of_element_located(browser.find_element_by_id('IdOfMyElement')))
			print "Page is ready!"
		except TimeoutException:
			print "Loading took too much time!"




		self.f1=cookies
		print cookies
		for cookie in cookies:
			#self.session.cookies.set(cookie['name'], cookie['value'],domain=cookie['domain'],expires=cookie['expiry'],path=cookie['path'],secure=cookie['secure'])
			self.session.cookies.set(cookie['name'], cookie['value'],domain=cookie['domain'])
		print self.session.cookies

		#soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")
jdlogin=JDLogin()
jdlogin.get_login_data()
ocookie=jdlogin.browser.get_cookies()
print ocookie==jdlogin.f1
