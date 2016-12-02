#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse

import requests
import json
import sys
import time
from datetime import datetime, timedelta
import grequests
import shell
import jdLogin
import re
reload(sys)
sys.setdefaultencoding("utf-8")

class jdSign(object):
    def __init__(self,sess):
        self.vipUrl=""
        self.vipJrUrl="http://vip.jr.jd.com/newSign/doSign"
        self.vip_home="http://vip.jd.com"
        self.vip_sign="http://vip.jd.com/common/signin.html"
        self.sess=sess

    def sign_vip(self):
        r=self.sess.get(self.vip_home)
        pattern=re.compile('''pageConfig\.token="(.*)"''')
        regmatch = re.search(pattern, r.content)
        self.token=regmatch.group(1)
        qs={"token":self.token}
        #print qs
        r=self.sess.get(self.vip_sign,params=qs)
        print r.text


    def sign_jrVip(self):
        r=self.sess.post(self.vipJrUrl,headers={"Referer":"http://vip.jr.jd.com/"})
        print r.text
        # try:
        #     jsonr=json.loads(r.text)
        #
        #     print jsonr['message']
        # except Exception,e:
        #     print  e
    def sign(self):
        self.sign_jrVip()
        self.sign_vip()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user file", default="user.txt")
    options = parser.parse_args()
    print options
    users= shell.get_user(options.user)

    sesss=[]
    #获取所有的用户登录cookie并创建session
    for user in users:
        req=requests.session()
        req.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
        })
        req.cookies=jdLogin.JDLogin(user[0],user[1]).get_logined_cookies()
        sesss.append(req)

    for sess in sesss:
        sign=jdSign(sess)
        sign.sign()
