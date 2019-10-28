#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     __init__.py
#   Author :        lumi
#   date：          2019/10/24
#   Description :
'''
import json
import requests
from odoorpc import ODOO

class OdooClient(object):
    '''
    通讯方式 client 登录->记录数据 api 接口调用
    '''

    def __init__(self, host, port, protocol, db, login, password):
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        self.url = '%s://%s:%s' % (scheme, host, port)
        self.db = db
        self.login = login
        self.password = password

    def json(self):
        pass


    def auth(self):
        pass


    def login(self):
        pass



class JsonRPC(object):

    def __init__(self, host, port, protocol, db, login, password):
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        self.url = '%s://%s:%s' % (scheme, host, port)
        self.db = db
        self.login = login
        self.password = password

    def post(self, api, **kwargs):
        request_data = {
            'params': {'db': self.db,
                       'login': self.login,
                       'password': self.password,
                       'kwargs': kwargs}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        url = '%s/%s'(self.url, api)
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        if not response:
            return
        response_json = json.loads(response.text)
        if response_json.get('error'):
            raise Exception(response_json.get('error').get('data').get('message'))
        result = json.loads(response_json.get('result'))
        if result.get('state', -1) != 0:
            raise Exception(result.get('msg'))
        data = result.get('printcontent')
        return data


