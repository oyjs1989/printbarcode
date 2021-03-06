#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     print_model
#   Author :        lumi
#   date：          2019/10/15
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import os
import json
from mycode128 import Code128Generate
from myean13 import EAN13Generate
from myqrcode import QrcodeGenerate
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtCore import QRect
from decimal import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import logging
from crccheck.crc import Crc
import re
import qrcode
import time

logger = logging.getLogger('logger')
LOCAK_TMP_IMAGE = 'print_image'
PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")

def get_font_path(file_path):
    if os.path.isfile(file_path):
        return file_path
    try:
        ImageFont.truetype(file_path, 10)
        return file_path
    except Exception:
        raise Exception('%s not found' % file_path)

def calc_crc(data):
    """
    计算crc值

    :param str data: 待校验的16进制数据

    Usage:
        >> calc_crc("AD8D69F1163A6ECDD546506D2E1F2FBB")
        6ee0
    """
    inst = Crc(16, 0x1021, initvalue=0xFFFF, xor_output=0xFFFF,
               reflect_input=True, reflect_output=True)
    inst.process(bytearray.fromhex(data))
    crc = inst.finalhex()
    return crc

def generate_new_zigbee(zigbee):
    zigbee = zigbee.replace('$s:','$S:')
    new_zigbee, DID, end = re.search('(.*\$D:)(\w*?)(%Z\$A:.*)', zigbee).groups()
    newdid = '%016x' % int(DID)   # 000000000F343FEE
    new_zigbee += newdid.upper()
    head, install_code = re.search('(.*\$I:)(\w*)', end).groups()
    new_zigbee += head
    new_zigbee += install_code[0:-4]
    CRC = calc_crc(install_code[0:-4]).upper()
    new_zigbee += CRC[-2:]
    new_zigbee += CRC[-4:-2]
    return new_zigbee


class Printer(object):
    '''
    打印机基类：
    0.获取打印配置  读取配置参数获取打印的内容格式
    1.生成打印模型  根据打印格式生成打印模型
    2.获取打印数据  向服务器/本地获取数据
    3.生成打印图像  填充数据生成图像
    4.调用打印机    调用打印机打印
    '''

    def __init__(self):
        '''
        init
        '''
        self.font_style = get_font_path('./Fonts/Arial.ttf')
        self.virtual_multiple = Decimal("100")  # 虚拟图像放大倍数
        self.virtual_width = self.virtual_multiple * Decimal("25.3")
        self.virtual_height = self.virtual_multiple * Decimal("25.8")
        self.reality_multiple = Decimal("3.78")  # 打印机放大倍数
        self.reality_heigh = round(Decimal('25.8') * self.reality_multiple)
        self.reality_width = round(Decimal('25.4') * self.reality_multiple)
        self.image = Image.new('L', (round(self.virtual_width), round(self.virtual_height)), 255)
        self.draw = ImageDraw.Draw(self.image)

    def get_print_info(self, input_context):
        '''

        :param input_context:
        :return:
        '''
        pass

    def generate_image(self):
        pass

    def print_image(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        logger.info(self.p)
        logger.info(self.print_device)
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        image = QPixmap()
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(0, 0, self.reality_width, self.reality_heigh), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束

    def run(self, input_context=None):
        start_time = time.time()
        self.get_print_info(self, input_context)
        self.generate_image(self)
        self.print_image()
        logger.info('%s: finished cost %s' % self.__class__, time.time() - start_time)

class NetPrinter(Printer):
    '''互联网信息打印'''
    pass

class LocalPrinter(Printer):
    '''
    本地打印，不需要互联网信息
    '''
    pass

class CloudPrinter(Printer):
    '''
    云打印  打印PDF/WORD/EXECL
    '''

    def loopping(self):
        self.run()

class ZigbeeQrcodeOnlyBig(LocalPrinter):

    MULTIPLE = Decimal("100")
    width = MULTIPLE * Decimal("16.0")
    height = MULTIPLE * Decimal("22.3")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    ZIGBEE_WIDTH = MULTIPLE * Decimal("14")
    ZIGBEE_HEIGHT = MULTIPLE * Decimal("14")

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/方正兰亭黑.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        request_data = {
            'params': {'db': odoo.env.db,
                       'login': odoo._login,
                       'password': odoo._password,
                       'sn': input_raw}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        host = odoo.host
        protocol = odoo.protocol
        port = odoo.port
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        url = '%s://%s:%s/api/post/iface/get/zigbee' % (scheme, host, port)
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        if not response:
            return
        response_json = json.loads(response.text)
        if response_json.get('error'):
            raise Exception(response_json.get('error').get('data').get('message'))
        result = json.loads(response_json.get('result'))
        # response = odoo.env['lumi.zigbee.information.wiazrd'].scan_sn_for_zigbee(input_raw)
        if result.get('state', -1) != 0:
            raise Exception(result.get('msg'))
        data = result.get('printcontent')
        zigbee_info = data.get('zigbee_info')
        # new_zigbee = generate_new_zigbee(zigbee_info)
        self.zigbee_draw(zigbee_info)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('22.6') * TIMES)
        width = round(Decimal('16') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, result.get('printcontent')))

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

    def zigbee_draw(self, zigbee):
        x = Decimal("1") * self.MULTIPLE
        y = Decimal("4.2") * self.MULTIPLE
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=0)
        qr.add_data(zigbee)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        im = image.resize((round(self.ZIGBEE_WIDTH), round(self.ZIGBEE_HEIGHT)), Image.ANTIALIAS)
        box = (x, y, x + self.ZIGBEE_WIDTH, y + self.ZIGBEE_HEIGHT)
        self.image.paste(im, box)

class SNPrintRectangle(LocalPrinter):
    '''
    SN本地打印矩形框
    '''
    multiple = Decimal("100")
    width = multiple * Decimal("34.5")
    height = multiple * Decimal("9.5")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    image = Image.new('L', (round(width), round(height)), 255)
    draw = ImageDraw.Draw(image)

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/Arial.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        if not input_raw:
            return
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.sn_draw(input_raw)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('9.5') * TIMES)
        width = round(Decimal('34.5') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0, center=False):
        y = top * self.multiple
        text_width, text_height = font.getsize(words)
        if margin_left:
            x = margin_left * self.multiple
        elif margin_right:
            x = self.width - margin_right * self.multiple - text_width
        elif center:
            x = (self.width - text_width) / 2
        else:
            x = 0
        self.draw.text((round(x), y), words, font=font, fill=0)

    def sn_draw(self, sn):
        x = Decimal("2.2") * self.multiple
        y = Decimal("1.25") * self.multiple
        width = self.multiple * Decimal("30.1")
        height = self.multiple * Decimal("5")
        cg = Code128Generate(sn, self.image, MULTIPLE=self.multiple)
        im = cg.get_pilimage(width, height)
        im = im.resize((round(width), round(height)), Image.ANTIALIAS)
        box = (x, y, x + width, y + height)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.PT_TO_MM_DECIMAL * Decimal("5.5")
        font = ImageFont.truetype(font_style, round(font_szie * self.multiple))
        self.write_word('SN:%s' % sn, font, top=Decimal('6.75'), center=True)


class SNPrintOval(LocalPrinter):
    '''
    SN本地打印36*10mm
    '''
    multiple = Decimal("100")
    width = multiple * Decimal("36")
    height = multiple * Decimal("10")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    image = Image.new('L', (round(width), round(height)), 255)
    draw = ImageDraw.Draw(image)

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/Arial.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        if not input_raw:
            return
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.sn_draw(input_raw)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('10') * TIMES)
        width = round(Decimal('36') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0, center=False):
        y = top * self.multiple
        text_width, text_height = font.getsize(words)
        if margin_left:
            x = margin_left * self.multiple
        elif margin_right:
            x = self.width - margin_right * self.multiple - text_width
        elif center:
            x = (self.width - text_width) / 2
        else:
            x = 0
        self.draw.text((round(x), y), words, font=font, fill=0)

    def sn_draw(self, sn):
        x = Decimal("4.1") * self.multiple
        y = Decimal("1") * self.multiple
        width = self.multiple * Decimal("27.8")
        height = self.multiple * Decimal("5.8")
        cg = Code128Generate(sn, self.image, MULTIPLE=self.multiple)
        im = cg.get_pilimage(width, height)
        im = im.resize((round(width), round(height)), Image.ANTIALIAS)
        box = (x, y, x + width, y + height)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.PT_TO_MM_DECIMAL * Decimal("5.5")
        font = ImageFont.truetype(font_style, round(font_szie * self.multiple))
        self.write_word(sn, font, top=Decimal('7.2'), center=True)


class ZigbeeQrcode(object):
    MULTIPLE = Decimal("100")
    width = MULTIPLE * Decimal("25.3")
    height = MULTIPLE * Decimal("25.8")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    ZIGBEE_WIDTH = MULTIPLE * Decimal("12.5")
    ZIGBEE_HEIGHT = MULTIPLE * Decimal("12.5")
    FONT_SZIE = PT_TO_MM_DECIMAL * Decimal("3.88")

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/Arial.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        request_data = {
            'params': {'db': odoo.env.db,
                       'login': odoo._login,
                       'password': odoo._password,
                       'sn': input_raw}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        host = odoo.host
        protocol = odoo.protocol
        port = odoo.port
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        url = '%s://%s:%s/api/post/iface/get/zigbee' % (scheme, host, port)
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
        zigbee_info = data.get('zigbee_info')
        # new_zigbee = generate_new_zigbee(zigbee_info)
        self.zigbee_draw(zigbee_info)
        self.sn_draw(input_raw)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('25.8') * TIMES)
        width = round(Decimal('25.4') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, result.get('printcontent')))

    def zigbee_draw(self, zigbee):
        x = Decimal("6.4") * self.MULTIPLE
        y = Decimal("0.5") * self.MULTIPLE
        # qr = QrcodeGenerate(zigbee, 'l')
        # image = qr.get_pilimage(10, width=0)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=0)
        qr.add_data(zigbee)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        im = image.resize((round(self.ZIGBEE_WIDTH), round(self.ZIGBEE_HEIGHT)), Image.ANTIALIAS)
        box = (x, y, x + self.ZIGBEE_WIDTH, y + self.ZIGBEE_HEIGHT)
        self.image.paste(im, box)

    def sn_draw(self, sn):
        cd = Code128Generate(sn, self.image, MULTIPLE=self.MULTIPLE)
        barcode_width = Decimal("20") * self.MULTIPLE
        barcode_height = Decimal("4.8") * self.MULTIPLE
        x = (self.width - barcode_width) / 2
        y = Decimal("13.5") * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.FONT_SZIE
        font = ImageFont.truetype(font_style, round(font_szie * self.MULTIPLE))
        self.write_word(sn, font, top=Decimal("18.5"), center=True)

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0, center=False):
        y = top * self.MULTIPLE
        text_width, text_height = font.getsize(words)
        if margin_left:
            x = margin_left * self.MULTIPLE
        elif margin_right:
            x = self.width - margin_right * self.MULTIPLE - text_width
        elif center:
            x = (self.width - text_width) / 2
        else:
            x = 0
        self.draw.text((round(x), y), words, font=font, fill=0)


class ZigbeeQrcodeOnly(object):
    MULTIPLE = Decimal("100")
    width = MULTIPLE * Decimal("16.0")
    height = MULTIPLE * Decimal("22.6")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    ZIGBEE_WIDTH = MULTIPLE * Decimal("12.5")
    ZIGBEE_HEIGHT = MULTIPLE * Decimal("12.5")
    FONT_SZIE = PT_TO_MM_DECIMAL * Decimal("3.4")

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/方正兰亭黑.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        request_data = {
            'params': {'db': odoo.env.db,
                       'login': odoo._login,
                       'password': odoo._password,
                       'sn': input_raw}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        host = odoo.host
        protocol = odoo.protocol
        port = odoo.port
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        url = '%s://%s:%s/api/post/iface/get/zigbee' % (scheme, host, port)
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        if not response:
            return
        response_json = json.loads(response.text)
        if response_json.get('error'):
            raise Exception(response_json.get('error').get('data').get('message'))
        result = json.loads(response_json.get('result'))
        # response = odoo.env['lumi.zigbee.information.wiazrd'].scan_sn_for_zigbee(input_raw)
        if result.get('state', -1) != 0:
            raise Exception(result.get('msg'))
        data = result.get('printcontent')
        zigbee_info = data.get('zigbee_info')
        # new_zigbee = generate_new_zigbee(zigbee_info)
        self.zigbee_draw(zigbee_info)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('22.6') * TIMES)
        width = round(Decimal('16') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, result.get('printcontent')))

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

    def zigbee_draw(self, zigbee):
        x = Decimal("1.75") * self.MULTIPLE
        y = Decimal("5.9") * self.MULTIPLE
        # qr = QrcodeGenerate(zigbee, 'l')
        # image = qr.get_pilimage(10, width=0)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=0)
        qr.add_data(zigbee)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        im = image.resize((round(self.ZIGBEE_WIDTH), round(self.ZIGBEE_HEIGHT)), Image.ANTIALIAS)
        box = (x, y, x + self.ZIGBEE_WIDTH, y + self.ZIGBEE_HEIGHT)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.FONT_SZIE
        font = ImageFont.truetype(font_style, round(font_szie * self.MULTIPLE))
        self.write_word('Install Code', font, top=Decimal('20'), margin_left=Decimal('4.35'))

class ZigbeeQrcodeBig(object):
    MULTIPLE = Decimal("100")
    width = MULTIPLE * Decimal("16.0")
    height = MULTIPLE * Decimal("22.6")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    ZIGBEE_WIDTH = MULTIPLE * Decimal("14")
    ZIGBEE_HEIGHT = MULTIPLE * Decimal("14")
    FONT_SZIE = PT_TO_MM_DECIMAL * Decimal("3.4")

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('./Fonts/方正兰亭黑.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        request_data = {
            'params': {'db': odoo.env.db,
                       'login': odoo._login,
                       'password': odoo._password,
                       'sn': input_raw}
        }
        headers = {
            'Content-Type': 'application/json',
        }
        host = odoo.host
        protocol = odoo.protocol
        port = odoo.port
        if protocol == 'jsonrpc':
            scheme = 'http'
        else:
            scheme = 'https'
        url = '%s://%s:%s/api/post/iface/get/zigbee' % (scheme, host, port)
        response = requests.post(url, data=json.dumps(request_data), headers=headers)
        if not response:
            return
        response_json = json.loads(response.text)
        if response_json.get('error'):
            raise Exception(response_json.get('error').get('data').get('message'))
        result = json.loads(response_json.get('result'))
        # response = odoo.env['lumi.zigbee.information.wiazrd'].scan_sn_for_zigbee(input_raw)
        if result.get('state', -1) != 0:
            raise Exception(result.get('msg'))
        data = result.get('printcontent')
        zigbee_info = data.get('zigbee_info')
        # new_zigbee = generate_new_zigbee(zigbee_info)
        self.zigbee_draw(zigbee_info)
        TIMES = Decimal("3.78")
        heigh = round(Decimal('22.6') * TIMES)
        width = round(Decimal('16') * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, result.get('printcontent')))

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0, x_center=False):
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

    def zigbee_draw(self, zigbee):
        x = Decimal("1") * self.MULTIPLE
        y = Decimal("4.2") * self.MULTIPLE
        # qr = QrcodeGenerate(zigbee, 'l')
        # image = qr.get_pilimage(10, width=0)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=0)
        qr.add_data(zigbee)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        im = image.resize((round(self.ZIGBEE_WIDTH), round(self.ZIGBEE_HEIGHT)), Image.ANTIALIAS)
        box = (x, y, x + self.ZIGBEE_WIDTH, y + self.ZIGBEE_HEIGHT)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.FONT_SZIE
        font = ImageFont.truetype(font_style, round(font_szie * self.MULTIPLE))
        self.write_word('Install Code', font, top=Decimal('19.8'), margin_left=Decimal('4.35'))


class XiaoMiPrinter_69(object):
    # 1in = 2.54cm = 25.4 mm = 72pt = 6pc
    MULTIPLE = Decimal("50")
    width = MULTIPLE * Decimal("33.8")
    height = MULTIPLE * Decimal("40.0")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    FONT_SZIE_HEAD = Decimal("4") * PT_TO_MM_DECIMAL
    FONT_SZIE_MID = Decimal("4.5") * PT_TO_MM_DECIMAL
    FONT_SZIE_CODE = Decimal("10") * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_LIFT = Decimal("4") * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_RIGHT = Decimal("3.18") * PT_TO_MM_DECIMAL

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE_BUTTOM = get_font_path('./Fonts/方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_HEAD = get_font_path('./Fonts/方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_CODE = get_font_path('./Fonts/Arial Unicode MS.TTF')
            self.FONT_STYLE_MID = get_font_path('./Fonts/Arial.ttf')
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
        first_name_y = Decimal("1.5")
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        text_width, text_height = font.getsize(first_name)
        self.write_word(first_name, font, top=first_name_y, margin_left=Decimal("2.5"))
        second_name_y = first_name_y + Decimal(text_height) / self.MULTIPLE
        self.write_word(second_name, font, top=second_name_y, margin_left=Decimal("2.5"))

    def color_draw(self, color):
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        color_y = Decimal("1.5")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(color, font, top=color_y, margin_right=Decimal("3.5"))

    def sn_draw(self, sn):
        cd = Code128Generate(sn, self.image, MULTIPLE=self.MULTIPLE)
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("5") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("5") * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)

    def sn_sku_draw(self, sn, sku):
        font_sytle = self.FONT_STYLE_MID
        font_szie = self.FONT_SZIE_MID
        y = Decimal("10.2")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        sn = 'SN:%s' % sn
        self.write_word(sn, font, top=y, margin_left=Decimal("2.5"))
        self.write_word(sku, font, top=y, margin_right=Decimal("3.5"))

    def barcode_draw(self, barcode):
        font_sytle = self.FONT_STYLE_CODE
        font_szie = self.FONT_SZIE_CODE
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        cd = EAN13Generate(barcode, self.image, font, MULTIPLE=self.MULTIPLE)
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("21") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("12.3") * self.MULTIPLE
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
            self.write_word(address, font, top=Decimal("32.6"), margin_left=Decimal("2.5"))
            self.write_word(date, font, top=Decimal("34.1"), margin_left=Decimal("2.5"))
        else:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            first_add = address[0:15]
            sec_add = "\t\t\t\t %s" % address[15:]
            self.write_word(first_add, font, top=Decimal("32.1"), margin_left=Decimal("2.5"))
            self.write_word(sec_add, font, top=Decimal("33.6"), margin_left=Decimal("2.5"))
            self.write_word(date, font, top=Decimal("35.3"), margin_left=Decimal("2.5"))

    def certificate_draw(self):
        self.draw.rectangle((round(Decimal("25.3") * self.MULTIPLE), round(Decimal("32.8") * self.MULTIPLE),
                             round(Decimal("30.5") * self.MULTIPLE), (round(Decimal("36") * self.MULTIPLE))),
                            outline="black",
                            width=round(Decimal("0.07") * self.MULTIPLE))
        font_sytle = self.FONT_STYLE_BUTTOM
        font_szie = self.FONT_SZIE_BUTTOM_RIGHT
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word('合格证', font, top=Decimal("33.2"), margin_right=Decimal("4.35"))
        self.write_word('已检验', font, top=Decimal("34.5"), margin_right=Decimal("4.35"))

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        response_json = odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(input_raw)
        if not response_json:
            return
        if response_json.get('state') != 0:
            raise Exception(response_json.get('msg'))

        def get_head_name(name):
            '''
            产品名称截取
            :param name:
            :return:
            '''
            count = 0
            first_name = name
            second_name = ''
            for char in name:
                if char in ('/', '-', ' '):
                    first_name = name[0:count]
                    second_name = name[count + 1:]
                    break
                else:
                    count += 1
            return first_name, second_name

        data = response_json.get('printcontent')
        first_name, second_name = get_head_name(data.get('product_name'))
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.name_draw(first_name, second_name)
        self.color_draw(data.get('color'))
        self.sn_draw(data.get('sn'))
        self.sn_sku_draw(data.get('sn'), data.get('SKU'))
        self.barcode_draw(data.get('barcode'))
        self.address_date_draw(data.get('address'), data.get('datetime'))
        self.certificate_draw()
        TIMES = Decimal("0.4")
        heigh = round(400 * TIMES)
        width = round(338 * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, response_json.get('printcontent')))


class AqaraPrinter_69(object):
    # 1in = 2.54cm = 25.4 mm = 72pt = 6pc
    MULTIPLE = Decimal("50")
    width = MULTIPLE * Decimal("33.8")
    height = MULTIPLE * Decimal("40.0")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    FONT_SZIE_HEAD = Decimal("4") * PT_TO_MM_DECIMAL
    FONT_SZIE_MID = Decimal("4.5") * PT_TO_MM_DECIMAL
    FONT_SZIE_CODE = Decimal("10") * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_LIFT = Decimal("4") * PT_TO_MM_DECIMAL
    FONT_SZIE_BUTTOM_RIGHT = Decimal("3.18") * PT_TO_MM_DECIMAL
    image = Image.new('L', (round(width), round(height)), 255)
    draw = ImageDraw.Draw(image)

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE_BUTTOM = get_font_path('./Fonts/方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_HEAD = get_font_path('./Fonts/方正兰亭黑_GBK.TTF')
            self.FONT_STYLE_CODE = get_font_path('./Fonts/Arial Unicode MS.TTF')
            self.FONT_STYLE_MID = get_font_path('./Fonts/Arial.ttf')
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
        first_name_y = Decimal("1.5")
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        text_width, text_height = font.getsize(first_name)
        self.write_word(first_name, font, top=first_name_y, margin_left=Decimal("2.5"))
        second_name_y = first_name_y + Decimal(text_height) / self.MULTIPLE
        self.write_word(second_name, font, top=second_name_y, margin_left=Decimal("2.5"))

    def color_draw(self, color):
        font_sytle = self.FONT_STYLE_HEAD
        font_szie = self.FONT_SZIE_HEAD
        color_y = Decimal("1.5")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(color, font, top=color_y, margin_right=Decimal("3.5"))

    def sn_draw(self, sn):
        cd = Code128Generate(sn, self.image, MULTIPLE=self.MULTIPLE)
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("5") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("4.7") * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)

    def sn_sku_draw(self, sn, sku):
        font_sytle = self.FONT_STYLE_MID
        font_szie = self.FONT_SZIE_MID
        y1 = Decimal("9.9")
        y2 = Decimal("11.9")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(sn, font, top=y1, margin_right=Decimal("3.5"))
        self.write_word(sku, font, top=y2, margin_right=Decimal("3.5"))

    def barcode_draw(self, barcode):
        font_sytle = self.FONT_STYLE_CODE
        font_szie = self.FONT_SZIE_CODE
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        cd = EAN13Generate(barcode, self.image, font, MULTIPLE=self.MULTIPLE)
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("19") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("13.8") * self.MULTIPLE
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
            self.write_word(address, font, top=Decimal("32.6"), margin_left=Decimal("2.5"))
            self.write_word(date, font, top=Decimal("34.1"), margin_left=Decimal("2.5"))
        else:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            first_add = address[0:15]
            sec_add = "\t\t\t\t %s" % address[15:]
            self.write_word(first_add, font, top=Decimal("32.1"), margin_left=Decimal("2.5"))
            self.write_word(sec_add, font, top=Decimal("33.6"), margin_left=Decimal("2.5"))
            self.write_word(date, font, top=Decimal("35.3"), margin_left=Decimal("2.5"))

    def certificate_draw(self):
        self.draw.rectangle((round(Decimal("25.3") * self.MULTIPLE), round(Decimal("32.8") * self.MULTIPLE),
                             round(Decimal("30.5") * self.MULTIPLE), (round(Decimal("36") * self.MULTIPLE))),
                            outline="black",
                            width=round(Decimal("0.07") * self.MULTIPLE))
        font_sytle = self.FONT_STYLE_BUTTOM
        font_szie = self.FONT_SZIE_BUTTOM_RIGHT
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word('合格证', font, top=Decimal("33.2"), margin_right=Decimal("4.35"))
        self.write_word('已检验', font, top=Decimal("34.5"), margin_right=Decimal("4.35"))

    def print_(self, odoo, input_raw=None):
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        if not input_raw:
            return
        response_json = odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(input_raw)
        if not response_json:
            return
        if response_json.get('state') != 0:
            raise Exception(response_json.get('msg'))

        def get_head_name(name):
            '''
            产品名称截取
            :param name:
            :return:
            '''
            num = 0
            count = 0
            first_name = name
            second_name = ''
            for char in name:
                if char in (' '):
                    if num == 1:
                        first_name = name[0:count]
                        second_name = name[count + 1:]
                        break
                    else:
                        num = 1
                count += 1
            return first_name, second_name

        data = response_json.get('printcontent')
        first_name, second_name = get_head_name(data.get('product_name'))
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.name_draw(first_name, second_name)
        self.color_draw(data.get('color'))
        self.sn_draw(data.get('sn'))
        self.sn_sku_draw(data.get('sn'), data.get('SKU'))
        self.barcode_draw(data.get('barcode'))
        self.address_date_draw(data.get('address'), data.get('datetime'))
        self.certificate_draw()
        TIMES = Decimal("0.4")
        heigh = round(400 * TIMES)
        width = round(338 * TIMES)
        x1 = 0
        y1 = 0
        x2 = x1 + width
        y2 = y1 + heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        self.image.save(LOCAK_TMP_IMAGE, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束
        logger.info('%s:%s' % (input_raw, response_json.get('printcontent')))


if __name__ == '__main__':
    s = generate_new_zigbee('G$M:1694$S:456SS111992900009$D:255167749%Z$A:04CF8CDF3C765017$I:163AF41829724ED328243F8A91C5179C8CF8')
    s = 'G$M:1694$S:456SS111992900009$D:000000000F358D05%Z$A:04CF8CDF3C765017$I:163AF41829724ED328243F8A91C5179CC548'
    qr = QrcodeGenerate(s, 'l')
    image = qr.get_pilimage(10, width=0)
    image.save('qrcode.png', 'png')