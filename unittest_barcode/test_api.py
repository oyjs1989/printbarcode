#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     test_communication
#   Author :        lumi
#   date：          2019/10/31
#   Description :   测试连接，测试
'''
# - Custom package

# - Third party module of python

# - import odoo package
from unittest import TestCase, main
import requests
import json
import jsonrpc

PRO_ERP = {'host': 'https://erp.aqara.com', 'username': 'miao.yu@aqara.com', 'password': '123123123',
           'db': 'erp'}
# XWD
PRO_MES = {'host': 'http://218.17.28.106:8069', 'username': 'junsong.ouyang@aqara.com', 'password': 'junsong123',
           'db': 'XWD_0411'}
# HTL
PRO_MES = {'host': 'http://202.104.22.108:8069', 'username': 'junsong.ouyang@aqara.com', 'password': 'junsong123',
           'db': '10c_mes'}

DEV_ERP = {'host': 'http://127.0.0.1:8069', 'username': 'admin', 'password': '123456', 'db': 'erp'}
DEV_MES = {'host': 'http://127.0.0.1:8069', 'username': '1111', 'password': '123456', 'db': ''}

MODE = 'pro'
SYSTEM = 'erp'

ERP_FUNC = ['zigbee']
MES_FUNC = ['barcode69']


class TestAPI(TestCase):

    def setUp(self) -> None:
        self.mode = MODE
        self.system = SYSTEM
        if self.mode == 'dev' and self.system == 'erp':
            self.db = DEV_ERP.get('db')
            self.username = DEV_ERP.get('username')
            self.password = DEV_ERP.get('password')
            self.host = DEV_ERP.get('host')
        elif self.mode == 'dev' and self.system == 'mes':
            self.db = DEV_MES.get('db')
            self.username = DEV_MES.get('username')
            self.password = DEV_MES.get('password')
            self.host = DEV_MES.get('host')
        elif self.mode == 'pro' and self.system == 'erp':
            self.db = PRO_ERP.get('db')
            self.username = PRO_ERP.get('username')
            self.password = PRO_ERP.get('password')
            self.host = PRO_ERP.get('host')
        elif self.mode == 'pro' and self.system == 'mes':
            self.db = PRO_MES.get('db')
            self.username = PRO_MES.get('username')
            self.password = PRO_MES.get('password')
            self.host = PRO_MES.get('host')
        else:
            return

        if self.system == 'mes':
            self.test_func = MES_FUNC
        else:
            self.test_func = ERP_FUNC

    def post_api(self, api, input_raw):
        request_data = {
            'params': {'db': self.db,
                       'login': self.username,
                       'password': self.password,
                       'sn': input_raw}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        url = '%s%s' % (self.host, api)
        print(url)
        print(request_data)
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        response_json = json.loads(response.text)
        print(response_json)
        return response_json

    def zigbee(self):
        api = '/api/post/iface/get/zigbee'
        response_json = self.post_api(api, '457/S1119A0800102')
        assert response_json.get('error') is None
        result = json.loads(response_json.get('result'))
        assert result.get('state') == 0
        data = result.get('printcontent')
        assert data != ''
        assert data.get('zigbee_info') == 'G$M:1695$S:457SS1119A0800102$D:255168460%Z$A:04CF8CDF3C7652DE$I:E5BDAB9AB74C5F6678AF9276DD20FFAA65DB'

    def barcode69(self):
        api = '/api/post/iface/get/zigbee'
        response_json = self.post_api(api, '457/S1119A0800102')
        if response_json.get('error'):
            raise Exception(response_json.get('error').get('data').get('message'))
        result = json.loads(response_json.get('result'))
        if result.get('state', -1) != 0:
            raise Exception(result.get('msg'))
        data = result.get('printcontent')
        assert data != ''

    def test_even(self):
        for func in self.test_func:
            if hasattr(self, func):
                getattr(self, func)()


if __name__ == '__main__':
    main()
