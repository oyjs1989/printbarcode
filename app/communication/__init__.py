#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     __init__.py
#   Author :        lumi
#   date：          2019/10/24
#   Description :
'''
import hashlib
import json
import requests
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode
import uuid
import time
from hmac import HMAC

MAC = uuid.UUID(int=uuid.getnode()).hex[-12:]


class OdooClient(object):
    '''
    通讯方式 client 登录->记录数据 api 接口调用
    '''

    __local_key = MAC

    def __init__(self, host, port, protocol, login, password, app_id=None, app_key=None):
        if protocol == 'd':
            scheme = 'http'
        else:
            scheme = 'https'
        self.url = '%s://%s:%s' % (scheme, host, port)
        self.login = login
        self.password = password
        self.app_id = app_id
        self.app_key = app_key

    def login(self):
        params = {
            'login': self.login,
            'password': self.password
        }
        pass

    def crontab(self):
        pass

    def remote_printer(self):
        api = '/api/post/remote/print'
        while True:
            time.sleep(2)
            data = self.jsonpost(api)

    def jsonpost(self, api, **kwargs):
        t_str = str(int(time.time()))
        request_data = {
            'params': {kwargs}
        }
        headers = {
            'Content-Type': 'application/json',
            "X-Appid": self.app_id,
            "X-Deviceid": "windows os client",
            "X-Timestamp": t_str
        }
        if self.app_id:
            headers['Authorization'] = self.authorization(api, request_data, headers)
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
        return result

    def pkcs7padding(self, text):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text

    def pkcs7unpadding(self, text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]

    def encrypt(self, key, content):
        """
        AES加密
        key,iv使用同一个
        模式cbc
        填充pkcs7
        :param key: 密钥
        :param content: 加密内容
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        iv = key_bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(b64encode(encrypt_bytes), encoding='utf-8')
        return result

    def decrypt(self, key, content):
        """
        AES解密
         key,iv使用同一个
        模式cbc
        去填充pkcs7
        :param key:
        :param content:
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        iv = key_bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # base64解码
        encrypt_bytes = b64decode(content)
        # 解密
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        # 重新编码
        result = str(decrypt_bytes, encoding='utf-8')
        # 去除填充内容
        result = self.pkcs7unpadding(result)
        return result

    def rsa_long_decrypt(self, msg, priv_key_str, default_length=128):
        """
        RSA分段解密公有方法,返回时会进行base64 encode
        1024bit的证书用128,priv_key需带有-----BEGIN RSA PRIVATE KEY-----开头及-----END RSA PRIVATE KEY-----结尾
        """
        msg = b64decode(msg)
        if "-----BEGIN RSA PRIVATE KEY-----" not in priv_key_str:
            priv_key_str = b64decode(priv_key_str)
        pri = RSA.importKey(priv_key_str)
        privobj = PKCS1_v1_5.new(pri)
        length = len(msg)
        if length < default_length:
            return b64encode("".join(privobj.decrypt(msg, 'xyz')))
        res = []
        offset = 0
        while length - offset > 0:
            if length - offset >= default_length:
                res.append(privobj.decrypt(msg[offset:offset + default_length], 'xyz'))
            else:
                res.append(privobj.decrypt(msg[offset:], 'xyz'))
            offset += default_length
        return b64encode("".join(res))

    def rsa_long_encrypt(self, msg, pub_key, default_length=117):
        """
        分段加密,返回时会进行base64encode
        :param msg:加密报文
        :param pub_key: 公钥(1024bit),需要带有-----BEGIN PUBLIC KEY-----开头及-----END PUBLIC KEY-----结尾
        :param default_length: 默认长度,1024bit使用117
        """
        if "-----BEGIN PUBLIC KEY-----" not in pub_key:
            pub_key = b64decode(pub_key)
        pub_rsa = RSA.importKey(pub_key)
        pub_obj = PKCS1_v1_5.new(pub_rsa)
        msg_length = len(msg)
        if msg_length < default_length:
            return b64encode("".join(pub_obj.encrypt(msg.encode('utf-8'))))
        offset = 0
        res = []
        while msg_length - offset > 0:
            if msg_length - offset > default_length:
                res.append((pub_obj.encrypt(msg[offset:offset + default_length])))
            else:
                res.append(pub_obj.encrypt(msg[offset:]))
            offset += default_length
        return b64encode("".join(res))

    def encrypt_all_attr(self):
        result = {}
        for k, v in self.__dict__.items():
            if 'cipher' in k:
                result[k] = self.encrypt(self.__key, v)
            else:
                result[k] = v
        return result

    def decrypt_all_attr(self, items):
        result = {}
        for k, v in items():
            if 'cipher' in k:
                result[k] = self.decrypt(self.__key, v)
            else:
                result[k] = v
        return result

    def authorization(self, api, request_json, headers):
        request_data = json.dumps(request_json, encoding="utf-8")
        body_hash = hashlib.sha256(request_data).hexdigest()
        # 生成签名
        data = "POST\n"
        data = data + api + "\n"
        data = data + "\n"
        # 必须将header中的key转为小写，保证签名正确
        headers_l = dict((k.lower(), v) for k, v in headers.iteritems())
        # 校验的header为 Content-Type, X-Appid, X-Timestamp, X-Deviceid
        if headers_l.has_key("x-appid") and headers_l.has_key("x-timestamp") and headers_l.has_key(
                "x-deviceid") and headers_l.has_key("content-type"):
            request_headers = {}
            request_headers["x-appid"] = headers_l.get("x-appid").strip()
            request_headers["x-timestamp"] = headers_l.get("x-timestamp").strip()
            request_headers["x-deviceid"] = headers_l.get("x-deviceid").strip()
            request_headers["content-type"] = headers_l.get("content-type").strip()
            sorted_headers = sorted(request_headers.iteritems(), key=lambda d: d[0])
        else:
            print("missing required headers")
            exit(-1)
        s_header = ""
        for (key, value) in sorted_headers:
            data = data + key + ":" + value + "\n"
            if s_header == "":
                s_header = key
            else:
                s_header = s_header + ";" + key
        data = data + s_header + "\n"
        data = data + body_hash
        # 生成签名
        hash_data = hashlib.sha256(data).hexdigest()
        return HMAC(self.app_key, hash_data, hashlib.sha256).hexdigest()
