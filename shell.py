#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse

import requests
import json
import sys
import time
from datetime import datetime
import grequests
reload(sys)
sys.setdefaultencoding("utf-8")


def get_user(file_name):
    with open(file_name,'r') as f:
        content=f.readlines()
        c_list=[i.strip() for i in content]
        d_list=[i.split(",") for i in c_list]
        return d_list

def get_urls(file_name):
    with open(file_name, 'r') as f:
        content = f.readlines()
        c_list = [i.strip() for i in content]
        return c_list
