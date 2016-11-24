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
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
import bs4
import re
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
	def __init__(self):
		self.session=requests.Session()

		self.browser = webdriver.PhantomJS()
		


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
		print self.session.cookies

		#soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")
jdlogin=JDLogin()
jdlogin.get_login_data()

