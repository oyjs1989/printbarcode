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

# - Third party module of python
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont, QIcon

# - import odoo package
from ui.body import Ui_Login
from ui.sn import Ui_SN

import resourcedata.images
from app.printwidgets.print_model import AqaraPrinter_69, XiaoMiPrinter_69, ZigbeeQrcode
import json

KEY = 'odoo'
IV = 'odoo'


class LocalConfig(object):
    # 本地缓存持久化

    PATH = os.path.join(os.environ.get('TEMP'), 'odoo')
    FILE = os.path.join(PATH, 'tmp')
    __key = bytes(KEY, encoding='utf-8')
    __iv = bytes(IV, encoding='utf-8')

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

    def encrypt(self, text):
        pass

    def decrypt(self, content):
        pass


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
            self.main.print(input_raw)
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
                '米家69码打印': XiaoMiPrinter_69(),
                'Aqara69码打印': AqaraPrinter_69(),
                'Zigbee&SN同页打印': ZigbeeQrcode(),
            }
        except Exception as e:
            self.show()
            QtWidgets.QMessageBox.warning(self, '异常', '字体文件未安装,请先安装字体或将字体文件放在运行文件相同文件夹下')
            sys.exit()
        self.actionLogin.triggered.connect(self.open_login)
        self.odoo = None
        self.config = LocalConfig()
        self.print_method_actions = self.create_menu_groups(self.menu_print_method, self.printers.keys(), self.select_print)
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
            raise e
            QtWidgets.QMessageBox.warning(self, '异常', '打印错误:%s' % e)

    def login(self, name, password, url):
        if not all([name, password, url]):
            QtWidgets.QMessageBox.warning(self, '异常', '填写内容不完整')
            raise Exception
        url_parse = urlparse(url)
        if url_parse.scheme == 'http':
            protocol = 'jsonrpc'
        else:
            protocol = 'jsonrpc+ssl'
        if ":" in url_parse.netloc:
            host, port = url_parse.netloc.split(':')
        else:
            host = url_parse.netloc
            port = 80
        try:
            odoo = odoorpc.ODOO(host=host, protocol=protocol, port=port)
            db = odoo.db.list()
            self.config.url = '%s://%s:%s' % (url_parse.scheme, host, port)
            if hasattr(self.config, 'urls'):
                self.config.urls = list(set(self.config.urls.append(self.config.url)))
            else:
                self.config.urls = [self.config.url]
            self.config.set_file_info()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '连接服务器失败')
            raise e
        try:
            odoo.login(db[0], name, password)
            self.odoo = odoo
            self.config.name = name
            if hasattr(self.config, 'names'):
                self.config.names = list(set(self.config.names.append(self.config.name)))
            else:
                self.config.names = [self.config.name]
            self.config.set_file_info()
            self.login_info = QtWidgets.QLabel()
            self.login_info.setText('用户名：%s 访问地址：%s' % (self.config.name, self.config.url))
            self.statusbar.addWidget(self.login_info)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '账号/密码错误')
            raise e


class LoginDialog(QtWidgets.QDialog, Ui_Login):

    def __init__(self, main):
        super(LoginDialog, self).__init__()
        self.setupUi(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
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
            self.namecompleter.setCaseSensitivity(Qt.CaseSensitive)
            self.name.setCompleter(self.namecompleter)

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
            QtWidgets.QMessageBox.warning(self, '提示', '登录成功')
        except Exception:
            pass
        self.hide()
