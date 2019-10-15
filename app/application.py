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
import odoorpc
from urllib.parse import urlparse
import json
from configparser import ConfigParser
# - Third party module of python
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
# - import odoo package
from ui.login import Ui_Login
from ui.main import Ui_main
import resourcedata.images
import sys
from app.printwidgets.printwidgets import ScanInput

KEY = 'odoo'
IV = 'odoo'


def get_print_cfg():
    config_path = os.path.join(os.getcwd(), 'config/print.cfg')
    if not os.path.exists(config_path):
        sys.exit()
    print_cfg = {}
    cfg = ConfigParser()
    cfg.read(config_path)
    for section in cfg.sections():
        print_cfg[section] = {'model': cfg.get(section, 'model'), 'method': cfg.get(section, 'method')}
    return print_cfg


PRINT_CFG = get_print_cfg()


def get_models_cfg():
    config_path = os.path.join(os.getcwd(), 'barcode_model')
    models = os.listdir(config_path)
    return models

MODELS_CFG = get_models_cfg()


class LocalConfig(object):
    # 本地缓存持久化

    PATH = os.path.join(os.environ.get('TEMP'), 'odoo')
    FILE = os.path.join(PATH, 'aqara_print_tmp')
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


class MainWindow(QtWidgets.QMainWindow, Ui_main):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QIcon(':/images/logo.png'))
        self.actionLogin.triggered.connect(self.open_login)
        self.print_method_actions = self.create_menu_groups(self.print_method, PRINT_CFG.keys(), self.select_print_method)
        self.print_model_actions = self.create_menu_groups(self.print_model, MODELS_CFG, self.select_print_model)
        self.actionselectbartenderpath.triggered.connect(self.input_bartender_path)
        self.odoo = None
        self.config = LocalConfig()
        self.menuERP.addAction(self.print_method.menuAction())
        self.inputline = ScanInput(self)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(22)
        self.inputline.setFont(font)
        self.inputline.setObjectName("inputline")
        self.gridLayout_2.addWidget(self.inputline, 0, 1, 1, 1)
        self.print_cfg = PRINT_CFG
        self.get_prev_config()

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

    def get_prev_config(self):
        if hasattr(self.config, 'print_model'):
            for action in self.print_model_actions.actions():
                if action.text() == self.config.print_model:
                    action.setChecked(True)
        if hasattr(self.config, 'print_method'):
            for action in self.print_method_actions.actions():
                if action.text() == self.config.print_method:
                    action.setChecked(True)

    def select_print_method(self, action):
        self.config.print_method = action.text()
        self.config.set_file_info()

    def select_print_model(self, action):
        self.config.print_model = action.text()
        self.config.print_model_path = os.path.join(os.getcwd(), 'barcode_model')
        self.config.set_file_info()

    def input_bartender_path(self):
        try:
            QtWidgets.QFileDialog.getExistingDirectory()
            get_directory_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选取BarTender文件夹",
                                 os.path.join(os.environ.get('PROGRAMFILES', 'C:\Program Files (x86)'), 'Seagull'))
        except Exception as e:
            return
        if not get_directory_path:
            return
        self.config.bartender_path = get_directory_path
        self.config.set_file_info()


    def open_login(self):
        self.login_dialog = LoginDialog(self)
        self.login_dialog.show()

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
            self.config.set_file_info()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '连接服务器失败')
            raise e
        try:
            odoo.login(db[0], name, password)
            self.odoo = odoo
            self.config.name = name
            self.config.set_file_info()
            self.login_info = QtWidgets.QLabel()
            # self.login_info.setObjectName("login_info")
            self.login_info.setText('用户名：%s 访问地址：%s' % (self.config.name, self.config.url))
            self.statusBar.addWidget(self.login_info)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '账号/密码错误')
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
