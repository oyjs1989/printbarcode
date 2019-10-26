#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo7_login
#   Author :        lumi
#   date：          2019/10/21
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
from odoorpc import ODOO

import requests
import json

# api = '/web/session/authenticate'
api = '/web/login'
# api = '/web'
# http = 'http://127.0.0.1:8069'
http = 'http://127.0.0.1:8069'

request_data = {
    'params': {
        # 'db': 'erp',
        'login': 'admin',
        'login_sucuess': 'admin',
        'password': '123456',
               }
}
headers = {'Content-Type': 'application/json'}
headers = {'Content-Type': 'application/http'}
url = '%s%s' % (http, api)
print(url)
response = requests.post(url, data=json.dumps(request_data), headers=headers)

print(response.cookies.get_dict())
print(response.text)
