#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     application
#   Author :        lumi
#   date：          2019/9/25
#   Description :
'''
# - Custom package
import os
import sys
import odoorpc
from urllib.parse import urlparse
import base64
from Crypto.Cipher import AES
from copy import deepcopy
import uuid

# - Third party module of python
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont, QIcon

# - import odoo package
from ui.body import Ui_Login
from ui.sn import Ui_SN

import resourcedata.images
from app.printwidgets.print_model import AqaraPrinter_69, XiaoMiPrinter_69, ZigbeeQrcode, ZigbeeQrcodeOnly, \
    SNPrintRectangle, SNPrintOval
import json



MAC = uuid.UUID(int=uuid.getnode()).hex[-12:]

class LocalConfig(object):
    # 本地缓存持久化

    PATH = os.path.join(os.environ.get('TEMP'), 'odoo')
    FILE = os.path.join(PATH, 'tmp')
    __key = bytes(MAC, encoding='utf-8')

    def __init__(self):
        self.get_file_info()

    def get_file_info(self):
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)

        if not os.path.exists(self.FILE):
            with open(self.FILE, 'w') as f:
                f.write(json.dumps(dict()))
                return
        else:
            with open(self.FILE, 'r') as f:
                context = json.load(f)
                for k, v in context.items():
                    setattr(self, k, v)

    def set_file_info(self):
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)
            with open(self.FILE, 'w') as f:
                f.write(json.dumps(dict()))
        with open(self.FILE, 'w') as f:
            json.dump(self.__dict__, f)

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
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
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
        encrypt_bytes = base64.b64decode(content)
        # 解密
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        # 重新编码
        result = str(decrypt_bytes, encoding='utf-8')
        # 去除填充内容
        result = self.pkcs7unpadding(result)
        return result

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


class SNInput(QtWidgets.QLineEdit):

    def __init__(self, main):
        super(SNInput, self).__init__()
        self.main = main

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            input_raw = self.text()
            self.setText('')
            if not self.main.odoo:
                QtWidgets.QMessageBox.information(self, '提示', '请先登录服务器')
                return
            if not input_raw:
                QtWidgets.QMessageBox.information(self, '提示', '输入为空')
                return
            self.main.print(input_raw.strip())
        else:
            QtWidgets.QLineEdit.keyPressEvent(self, event)


class MainWindow(QtWidgets.QMainWindow, Ui_SN):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.sn_input = SNInput(self)
        self.sn_input.setObjectName("sn_input")
        font = QFont()
        font.setPointSize(25)
        self.sn_input.setFont(font)
        self.horizontalLayout.addWidget(self.sn_input)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QIcon(':/images/logo.png'))
        try:
            self.printers = {
                '69码打印:米家': XiaoMiPrinter_69(),
                '69码打印:Aqara': AqaraPrinter_69(),
                'Zigbee:SN同页打印': ZigbeeQrcode(),
                'Zigbee:二维码打印': ZigbeeQrcodeOnly(),
                'SN打印:34.5*9.5mm': SNPrintRectangle(),
                'SN打印:36*10mm': SNPrintOval(),
            }
        except Exception as e:
            self.show()
            QtWidgets.QMessageBox.warning(self, '异常', '字体文件未安装,请先安装字体或将字体文件放在运行文件相同文件夹下')
            sys.exit()
        self.actionLogin.triggered.connect(self.open_login)
        self.odoo = None
        self.config = LocalConfig()
        self.print_method_actions = self.create_menu_groups(self.menu_print_method, self.printers.keys(),
                                                            self.select_print)
        self.loading_historical_data()

    def loading_historical_data(self):
        if hasattr(self.config, 'print_method'):
            for action in self.print_method_actions.actions():
                if action.text() == self.config.print_method:
                    action.setChecked(True)

    def create_menu_groups(self, menu, actions, func):
        action_groups = QtWidgets.QActionGroup(self)
        for action in actions:
            qtaction = QtWidgets.QAction(self)
            qtaction.setObjectName(action)
            qtaction.setText(action)
            qtaction.setCheckable(True)
            menu.addAction(action_groups.addAction(qtaction))
        action_groups.isExclusive()
        action_groups.triggered.connect(func)
        return action_groups

    def select_print(self, action):
        self.config.print_method = action.text()
        self.config.set_file_info()

    def open_login(self):
        self.login_dialog = LoginDialog(self)
        self.login_dialog.show()

    def print(self, input_raw):
        try:
            if not hasattr(self.config, 'print_method'):
                QtWidgets.QMessageBox.warning(self, '异常', '未选择打印方法')
                return
            printer = self.printers.get(self.config.print_method)
            printer.print_(self.odoo, input_raw)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '打印错误:%s' % e)

    def login(self, name, password, url):
        if not all([name, password, url]):
            QtWidgets.QMessageBox.warning(self, '异常', '填写内容不完整')
            raise Exception
        url_parse = urlparse(url)
        if ":" in url_parse.netloc:
            host, port = url_parse.netloc.split(':')
        else:
            host = url_parse.netloc
            port = 80
        if url_parse.scheme == 'http':
            protocol = 'jsonrpc'
        else:
            protocol = 'jsonrpc+ssl'
            port = 443
        try:
            self.config.url = '%s://%s:%s' % (url_parse.scheme, host, port)
            self.config.set_file_info()
            odoo = odoorpc.ODOO(host=host, protocol=protocol, port=port)
            db = odoo.db.list()
            if hasattr(self.config, 'urls'):
                self.config.urls.append(self.config.url)
                self.config.urls = list(set(self.config.urls))
            else:
                self.config.urls = [self.config.url]
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '连接服务器失败：%s' % str(e))
            return
        try:
            # erp获取不了数据库名称
            if 'erp' in host:
                db = ['erp']
            odoo.login(db[0], name, password)
            self.odoo = odoo
            self.config.name = name
            if hasattr(self.config, 'names'):
                self.config.names.append(self.config.name)
                self.config.names = list(set(self.config.names))
            else:
                self.config.names = [self.config.name]
            self.config.set_file_info()
            if hasattr(self, 'login_info'):
                self.login_info.setText('用户名：%s 访问地址：%s' % (self.config.name, self.config.url))
            else:
                self.login_info = QtWidgets.QLabel()
                self.login_info.setText('用户名：%s 访问地址：%s' % (self.config.name, self.config.url))
                self.statusbar.addWidget(self.login_info)
                QtWidgets.QMessageBox.warning(self, '提示', '登录成功')
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '登录错误:%s' % e)
            raise e


class LoginDialog(QtWidgets.QDialog, Ui_Login):

    def __init__(self, main):
        super(LoginDialog, self).__init__()
        self.setupUi(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.main = main
        # 历史url和账号
        if hasattr(self.main.config, 'url'):
            self.net.setText(self.main.config.url)
        if hasattr(self.main.config, 'name'):
            self.name.setText(self.main.config.name)
        if hasattr(self.main.config, 'urls'):
            urls = self.main.config.urls
            self.urlcompleter = QtWidgets.QCompleter(urls)
            self.net.setCompleter(self.urlcompleter)
        if hasattr(self.main.config, 'names'):
            names = self.main.config.names
            self.namecompleter = QtWidgets.QCompleter(names)
            self.namecompleter.setCaseSensitivity(Qt.CaseSensitive)  # 设置区分大小写
            self.name.setCompleter(self.namecompleter)
        # self.setWindowFlags(Qt.WindowMinimizeButtonHint |  # 使能最小化按钮
        #                     Qt.WindowCloseButtonHint |  # 使能关闭按钮
        #                     Qt.WindowStaysOnTopHint)

        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QIcon(':/images/logo.png'))
        btns = self.buttonBox.buttons()
        btns[0].setText('确认')
        btns[1].setText('取消')

    @pyqtSlot()
    def accept(self):
        password = self.password.text()
        name = self.name.text()
        url = self.net.text()
        try:
            self.main.login(name, password, url)
        except Exception:
            pass
        self.hide()
