#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import argparse

import requests

import jdLogin

parser = argparse.ArgumentParser(description='模拟京东登录')
parser.add_argument('-u', '--username')
parser.add_argument('-p', '--password')
options = parser.parse_args()

jdlogin = jdLogin.JDLogin(options.username, options.password)
print jdlogin.get_logined_cookies()
