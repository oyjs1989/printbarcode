#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     application
#   Author :        lumi
#   date：          2019/9/25
#   Description :
'''
# - Custom package
from decimal import *
import os
import sys
import odoorpc
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import urlparse

# - Third party module of python
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QUrl, QSizeF, QRect, Qt, QSize
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtGui import QPainter, QPixmap, QFont, QIcon

# - import odoo package
from ui.body import Ui_Login
from ui.sn import Ui_SN
from mycode128 import Code128Generate
from myean13 import EAN13Generate
from datetime import datetime
import resourcedata.images
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

def get_font_path(file_path):
    if os.path.isfile(file_path):
        return file_path
    try:
        ImageFont.truetype(file_path, 10)
        return file_path
    except Exception:
        raise Exception('%s not found' % file_path)

class Printer(object):

    # 1in = 2.54cm = 25.4 mm = 72pt = 6pc
    MULTIPLE = Decimal('50')
    width = MULTIPLE * Decimal('33.8')
    height = MULTIPLE * Decimal('40.0')
    PT_TO_MM_DECIMAL = Decimal('25.4') / Decimal('72')
    FONT_SZIE_HEAD = Decimal('4') * PT_TO_MM_DECIMAL
    FONT_SZIE_MID = Decimal('4.5') * PT_TO_MM_DECIMAL
    FONT_SZIE_CODE = Decimal('10') * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_LIFT = Decimal('4') * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_RIGHT = Decimal('3.18') * PT_TO_MM_DECIMAL
    image = Image.new('L', (round(width), round(height)), 255)
    draw = ImageDraw.Draw(image)

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE_BUTTOM = get_font_path('方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_HEAD = get_font_path('方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_CODE = get_font_path('Arial Unicode MS.TTF')
            self.FONT_STYLE_MID = get_font_path('Arial.ttf')
        except Exception as e:
            raise e
        # self.print_device.setPaperSize(QSizeF(400, 338), QPrinter.Point) #设置打印机数据

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0):
        y = top * self.MULTIPLE
        text_width, text_height = font.getsize(words)
        if margin_left:
            x = margin_left * self.MULTIPLE
        elif margin_right:
            x = self.width - margin_right * self.MULTIPLE - text_width
        else:
            x = 0
        self.draw.text((round(x), y), words, font=font, fill=0)
        return Decimal(text_height) / self.MULTIPLE

    def name_draw(self, first_name, second_name):
        first_name_y = Decimal('1.5')
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        text_width, text_height = font.getsize(first_name)
        self.write_word(first_name, font, top=first_name_y, margin_left=Decimal('2.5'))
        second_name_y = first_name_y + Decimal(text_height) / self.MULTIPLE
        self.write_word(second_name, font, top=second_name_y, margin_left=Decimal('2.5'))

    def color_draw(self, color):
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        color_y = Decimal('1.5')
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(color, font, top=color_y, margin_right=Decimal('3.5'))

    def sn_draw(self, sn):
        cd = Code128Generate(sn, self.image, options={'MULTIPLE': self.MULTIPLE})
        barcode_width = Decimal('27.8') * self.MULTIPLE
        barcode_height = Decimal('5') * self.MULTIPLE
        x = Decimal('2.5') * self.MULTIPLE
        y = Decimal('5') * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)

    def sn_sku_draw(self, sn, sku=None):
        font_sytle = self.FONT_STYLE_MID
        font_szie = self.FONT_SZIE_MID
        y = Decimal('10.2')
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        if sku:
            self.write_word(sn, font, top=y, margin_left=Decimal('2.5'))
            self.write_word(sku, font, top=y, margin_right=Decimal('3.5'))
        else:
            self.write_word(sn, font, top=y, margin_right=Decimal('3.5'))

    def barcode_draw(self, barcode):
        font_sytle = self.FONT_STYLE_CODE
        font_szie = self.FONT_SZIE_CODE
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        cd = EAN13Generate(barcode, self.image, font, options={'MULTIPLE': self.MULTIPLE})
        barcode_width = Decimal('27.8') * self.MULTIPLE
        barcode_height = Decimal('21') * self.MULTIPLE
        x = Decimal('2.5') * self.MULTIPLE
        y = Decimal('12.3') * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)

    def address_date_draw(self, address, date):
        address = address.strip()
        # 地址超过 14个换行
        if len(address) <= 14:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            self.write_word(address, font, top=Decimal('32.6'), margin_left=Decimal('2.5'))
            self.write_word(date, font, top=Decimal('34.1'), margin_left=Decimal('2.5'))
        else:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            first_add = address[0:15]
            sec_add = "\t\t\t\t %s" % address[15:]
            self.write_word(first_add, font, top=Decimal('32.1'), margin_left=Decimal('2.5'))
            self.write_word(sec_add, font, top=Decimal('33.6'), margin_left=Decimal('2.5'))
            self.write_word(date, font, top=Decimal('35.3'), margin_left=Decimal('2.5'))

    def certificate_draw(self):
        self.draw.rectangle((round(Decimal('25.3') * self.MULTIPLE), round(Decimal('32.8') * self.MULTIPLE),
                        round(Decimal('30.5') * self.MULTIPLE), (round(Decimal('36') * self.MULTIPLE))), outline="black",
                       width=round(Decimal('0.07') * self.MULTIPLE))
        font_sytle = self.FONT_STYLE_BUTTOM
        font_szie = self.FONT_SZIE_BUTTOM_RIGHT
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word('合格证', font, top=Decimal('33.2'), margin_right=Decimal('4.35'))
        self.write_word('已检验', font, top=Decimal('34.5'), margin_right=Decimal('4.35'))

    def print_(self, data=None):
        if not data:
            return
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.name_draw(data.get('first_name'), data.get('second_name'))
        self.color_draw(data.get('color'))
        self.sn_draw(data.get('sn'))
        if '小米' in data.get('first_name'):
            self.sn_sku_draw(data.get('sn'), data.get('SKU'))
        else:
            self.sn_sku_draw(data.get('sn'))
        self.barcode_draw(data.get('barcode'))
        self.address_date_draw(data.get('address'), data.get('datetime'))
        self.certificate_draw()

        TIMES = Decimal('0.4')
        # image_data = open('./code.jpg', 'rb').read()
        # image_content = base64.b64decode(data_url)  # 数据流base64解码
        # image = QImage()
        heigh = round(400*TIMES)
        width = round(338*TIMES)
        x1 = 0
        y1 = 0
        x2 = x1+width
        y2 = y1+heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        # image.load(tmp)
        # image.load('./code.jpg')
        # image = image.scaled(QSize(width, heigh), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        # painter.drawImage(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束

class SNInput(QtWidgets.QLineEdit):

    def __init__(self, main):
        super(SNInput, self).__init__()
        self.main = main

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            sn = self.text()
            self.setText('')
            if not self.main.odoo:
                QtWidgets.QMessageBox.information(self, '提示', '请先登录服务器')
                return
            if not sn:
                QtWidgets.QMessageBox.information(self, '提示', 'SN为空')
                return
            info = self.main.get_info(sn)
            if info.get('state') == 0:
                self.main.print(info.get('printcontent'))
            elif info.get('state') == 1:
                QtWidgets.QMessageBox.information(self, '提示', '未找到对应SN')
            else:
                QtWidgets.QMessageBox.warning(self, '异常', '获取69码数据错误:%s' % info.get('msg'))
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
            self.printer = Printer()
        except Exception as e:
            self.show()
            QtWidgets.QMessageBox.warning(self, '异常', '字体文件未安装,请先安装字体或将字体文件放在运行文件相同文件夹下')
            sys.exit()
        self.actionLogin.triggered.connect(self.open_login)
        self.odoo = None
        self.config = LocalConfig()

    def get_info(self, sn):
        try:
            info = self.odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(sn)
        except Exception as e:
            return {'state': -1, 'msg': e}
        return info

    def open_login(self):
        self.login_dialog = LoginDialog(self)
        self.login_dialog.show()


    def print(self, info):
        try:
            self.printer.print_(info)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '打印69码错误:%s' % e)

    def login(self, name, password, url):
        self.config.name = name
        self.config.url = url
        self.config.set_file_info()
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
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '异常', '连接服务器失败')
            raise e
        try:
            odoo.login(db[0], name, password)
            self.odoo = odoo
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
