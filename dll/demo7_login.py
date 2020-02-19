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
import xmlrpc
import requests
import json
import odoorpc

protocol = 'jsonrpc+ssl'
port = 443
odoo = odoorpc.ODOO(host='http://erp.aqara.com', protocol=protocol, port=port)
print(odoo.db.list())

# client = xmlrpc.client()

# api = '/web/session/authenticate'
# api = '/web/login'
# api = '/web'
# api = '/web/webclient/version_info'
# login = 'http://127.0.0.1:8069/web/session/authenticate'
# get_session_info = 'http://127.0.0.1:8069/web/session/get_session_info'

# http = 'http://127.0.0.1:8069/web?db'
# http = 'https://erp.aqara.com/web?db'

# request_data = {
#     'params': {
#     }
# }
# http = 'https://erp.aqara.com/web/database/list'
# http = 'http://127.0.0.1:8069/web/database/list'
# headers = {'Content-Type': 'application/json'}
# response = requests.post(http, data=json.dumps(request_data), headers=headers)
# print(response.cookies.get_dict())
# print(response.text)
# cookies = response.cookies.get_dict()
#
# check = 'http://127.0.0.1:8069/web/session/check'
# request_data = {
#     'params': {
#         # 'db': 'erp',
#         # 'login': 'admin',
#         # 'login_sucuess': 'admin',
#         # 'password': '123456',
#     }
# }
# headers = {'Content-Type': 'application/json'}
# response = requests.get(check, data=json.dumps(request_data), headers=headers, cookies=cookies)
# print(response.cookies.get_dict())
# print(response.text)

# request_data = {
#     'params': {
#         'db': 'erp',
#         'login': 'admin',
#         # 'login_sucuess': 'admin',
#         'password': '123456',
#         # 'login_sucuess': False,
#     }
# }
# response = requests.post(login, data=json.dumps(request_data), headers=headers)
# print(response.cookies.get_dict())
# print(response.text)
