#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo_post
#   Author :        lumi
#   date：          2019/11/26
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package

import requests
import json
import time
host = '127.0.0.1'
protocol = 'jsonrpc'
port = '8069'

host = 'erp.aqara.com'
protocol = 'https'
port = '443'

request_data = {
    'params': {'db': 'erp',
               'login': 'miao.yu@aqara.com',
               'password': '123123123',
               'sn': '325/00000522'}
}
headers = {
    'Content-Type': 'application/json',
}

if protocol == 'jsonrpc':
    scheme = 'http'
else:
    scheme = 'https'
url = '%s://%s:%s/api/post/iface/get/zigbee' % (scheme, host, port)
print(url)
start_time = time.time()
response = requests.post(url, data=json.dumps(request_data), headers=headers, timeout=100)
if not response:
    exit()
response_json = json.loads(response.text)
print(response_json)
if response_json.get('error'):
    raise Exception(response_json.get('error').get('data').get('message'))
result = json.loads(response_json.get('result'))
end_time = time.time()
print(end_time-start_time)

