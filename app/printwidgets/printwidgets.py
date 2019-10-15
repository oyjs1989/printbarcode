#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     print
#   Author :        lumi
#   date：          2019/10/10
#   Description :
'''
# - Custom package
import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import clr

MEHTOD = {
    '69码打印': {
        'model': 'wizard.mrp.commodity.barcode', 'method': 'print_commodity_barcode'
    }
}

clr.FindAssembly("PrintDll.dll")  ## 加载c#dll文件
from PrintDll import *  # 导入命名空间


class BartenderPrinter(object):
    instance = Print()

    def _print(self, barcode, bartender_path, model_path, barcode_model):
        self.instance.PrintBarcode(barcode, bartender_path, model_path, barcode_model)  # class1是dll里面的类
        # self.instance.PrintBarcode('123456789123', r'C:\Program Files (x86)\Seagull\BarTender Suite', r'C:\Users\lumi\Desktop', 'demo.btw')  # class1是dll里面的类


Printer = BartenderPrinter()

class ScanInput(QtWidgets.QLineEdit):

    def __init__(self, main):
        super(ScanInput, self).__init__()
        self.main = main
        self.printer = Printer

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            input = self.text()
            self.setText('')
            if not self.main.odoo:
                QtWidgets.QMessageBox.information(self, '提示', '请先登录服务器')
                return
            if not input:
                QtWidgets.QMessageBox.information(self, '提示', '输入值为空')
                return
            self.print_(input)
        else:
            QtWidgets.QLineEdit.keyPressEvent(self, event)

    def print_(self, input):
        try:
            if not hasattr(self.main.config, 'bartender_path'):
                QtWidgets.QMessageBox.information(self, '错误', '参数BarTender未设置')
                return
            if not hasattr(self.main.config, 'print_method'):
                QtWidgets.QMessageBox.information(self, '错误', '参数打印方法未设置')
                return
            if not hasattr(self.main.config, 'print_model'):
                QtWidgets.QMessageBox.information(self, '错误', '参数打印模型未设置')
                return
            info = self.get_data(input)
            if not info:
                QtWidgets.QMessageBox.information(self, '提示', '未找到对应信息请检查编码')
                return
            info = '小米米家智能门锁,标准锁体 40~80mm门厚,颜色：碳素黑,21379/00048293,SKU:SZB4022CN,6934177714108,生产地址：广东省佛山市南海区,生产日期：2019.09'
            self.printer._print(info, self.main.config.bartender_path, self.main.config.print_model_path,self.main.config.print_model)
        except Exception as e:
            QtWidgets.QMessageBox.information(self, '提示', str(e))
            return

    def get_data(self, input):
        # return self.main.odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(input)
        server_model = self.main.print_cfg[self.main.config.print_method].get('model')
        server_method = self.main.print_cfg[self.main.config.print_method].get('method')
        if server_model and server_method:
            return getattr(self.main.odoo.env[server_model], server_method)(input)
        else:
            return input
