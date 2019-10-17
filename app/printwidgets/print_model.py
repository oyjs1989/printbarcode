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

from mycode128 import Code128Generate
from myean13 import EAN13Generate
from myqrcode import QrcodeGenerate
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtCore import QRect
from decimal import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def get_font_path(file_path):
    if os.path.isfile(file_path):
        return file_path
    try:
        ImageFont.truetype(file_path, 10)
        return file_path
    except Exception:
        raise Exception('%s not found' % file_path)


class ZigbeeQrcode(object):
    MULTIPLE = Decimal("100")
    width = MULTIPLE * Decimal("25.3")
    height = MULTIPLE * Decimal("25.8")
    PT_TO_MM_DECIMAL = Decimal("25.4") / Decimal("72")
    ZIGBEE_WIDTH = MULTIPLE * Decimal("12.5")
    ZIGBEE_HEIGHT = MULTIPLE * Decimal("12.5")
    FONT_SZIE = PT_TO_MM_DECIMAL * Decimal("3.88")
    image = Image.new('L', (round(width), round(height)), 255)
    draw = ImageDraw.Draw(image)

    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        try:
            self.FONT_STYLE = get_font_path('Arial.ttf')
        except Exception as e:
            raise e

    def print_(self, odoo, input_raw=None):
        if not input_raw:
            return
        response = odoo.env['lumi.zigbee.information.wiazrd'].scan_sn_for_zigbee(input_raw)
        if not response:
            return
        if response.get('state') != 0:
            raise Exception(response.get('msg'))
        data = response.get('printcontent')
        self.zigbee_draw(data.get('zigbee_info'))
        self.sn_draw(input_raw)
        TIMES = Decimal("3.75")
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

    def zigbee_draw(self, zigbee):
        x = Decimal("6.4") * self.MULTIPLE
        y = Decimal("0.5") * self.MULTIPLE
        qr = QrcodeGenerate(zigbee, 'h')
        image = qr.get_pilimage(10,colour=1, width=1)
        im = image.resize((round(self.ZIGBEE_WIDTH), round(self.ZIGBEE_HEIGHT)), Image.ANTIALIAS)
        box = (x, y, x + self.ZIGBEE_WIDTH, y + self.ZIGBEE_HEIGHT)
        self.image.paste(im, box)

    def sn_draw(self, sn):
        cd = Code128Generate(sn, self.image, options={'MULTIPLE': self.MULTIPLE})
        barcode_width = Decimal("19.8") * self.MULTIPLE
        barcode_height = Decimal("5.8") * self.MULTIPLE
        x = (self.width - barcode_width) / 2
        y = Decimal("14") * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)
        font_style = self.FONT_STYLE
        font_szie = self.FONT_SZIE
        font = ImageFont.truetype(font_style, round(font_szie * self.MULTIPLE))
        self.write_word(sn, font, top=Decimal("20"), center=True)

    def write_word(self, words, font, top=0, margin_left=0, margin_right=0, center=False):
        y = top * self.MULTIPLE
        text_width, text_height = font.getsize(words)
        if margin_left:
            x = margin_left * self.MULTIPLE
        elif margin_right:
            x = self.width - margin_right * self.MULTIPLE - text_width
        elif center:
            x = (self.width - text_width)/2
        else:
            x = 0
        self.draw.text((round(x), y), words, font=font, fill=0)


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
        cd = Code128Generate(sn, self.image, options={'MULTIPLE': self.MULTIPLE})
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("5") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("5") * self.MULTIPLE
        box = (x, y, x + barcode_width, y + barcode_height)
        im = cd.get_pilimage(barcode_width, barcode_height)
        self.image.paste(im, box)

    def sn_sku_draw(self, sn,sku):
        font_sytle = self.FONT_STYLE_MID
        font_szie = self.FONT_SZIE_MID
        y = Decimal("10.2")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(sn, font, top=y, margin_left=Decimal("2.5"))
        self.write_word(sku, font, top=y, margin_right=Decimal("3.5"))

    def barcode_draw(self, barcode):
        font_sytle = self.FONT_STYLE_CODE
        font_szie = self.FONT_SZIE_CODE
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        cd = EAN13Generate(barcode, self.image, font, options={'MULTIPLE': self.MULTIPLE})
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
            self.write_word(address, font, top=Decimal("32.6'), margin_left=Decimal('2.5"))
            self.write_word(date, font, top=Decimal("34.1'), margin_left=Decimal('2.5"))
        else:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            first_add = address[0:15]
            sec_add = "\t\t\t\t %s" % address[15:]
            self.write_word(first_add, font, top=Decimal("32.1'), margin_left=Decimal('2.5"))
            self.write_word(sec_add, font, top=Decimal("33.6'), margin_left=Decimal('2.5"))
            self.write_word(date, font, top=Decimal("35.3'), margin_left=Decimal('2.5"))

    def certificate_draw(self):
        self.draw.rectangle((round(Decimal("25.3") * self.MULTIPLE), round(Decimal("32.8") * self.MULTIPLE),
                        round(Decimal("30.5") * self.MULTIPLE), (round(Decimal("36") * self.MULTIPLE))), outline="black",
                       width=round(Decimal("0.07") * self.MULTIPLE))
        font_sytle = self.FONT_STYLE_BUTTOM
        font_szie = self.FONT_SZIE_BUTTOM_RIGHT
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word('合格证', font, top=Decimal("33.2'), margin_right=Decimal('4.35"))
        self.write_word('已检验', font, top=Decimal("34.5'), margin_right=Decimal('4.35"))

    def print_(self, odoo, input_raw=None):
        if not input_raw:
            return
        response = odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(input_raw)
        if not response:
            return
        if response.get('state') != 0:
            return
        data = response.get('printcontent')
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.name_draw(data.get('first_name'), data.get('second_name'))
        self.color_draw(data.get('color'))
        self.sn_draw(data.get('sn'))
        self.sn_sku_draw(data.get('sn'), data.get('SKU'))
        self.barcode_draw(data.get('barcode'))
        self.address_date_draw(data.get('address'), data.get('datetime'))
        self.certificate_draw()
        TIMES = Decimal("0.4")
        heigh = round(400*TIMES)
        width = round(338*TIMES)
        x1 = 0
        y1 = 0
        x2 = x1+width
        y2 = y1+heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束

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
        cd = Code128Generate(sn, self.image, options={'MULTIPLE': self.MULTIPLE})
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
        y1 = Decimal("10.2")
        y2 = Decimal("12.2")
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word(sn, font, top=y1, margin_right=Decimal("3.5"))
        self.write_word(sku, font, top=y2, margin_right=Decimal("3.5"))

    def barcode_draw(self, barcode):
        font_sytle = self.FONT_STYLE_CODE
        font_szie = self.FONT_SZIE_CODE
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        cd = EAN13Generate(barcode, self.image, font, options={'MULTIPLE': self.MULTIPLE})
        barcode_width = Decimal("27.8") * self.MULTIPLE
        barcode_height = Decimal("19") * self.MULTIPLE
        x = Decimal("2.5") * self.MULTIPLE
        y = Decimal("14.3") * self.MULTIPLE
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
            self.write_word(address, font, top=Decimal("32.6'), margin_left=Decimal('2.5"))
            self.write_word(date, font, top=Decimal("34.1'), margin_left=Decimal('2.5"))
        else:
            font_sytle = self.FONT_STYLE_BUTTOM
            font_szie = self.FONT_SZIE_BUTTOM_LIFT
            font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
            first_add = address[0:15]
            sec_add = "\t\t\t\t %s" % address[15:]
            self.write_word(first_add, font, top=Decimal("32.1'), margin_left=Decimal('2.5"))
            self.write_word(sec_add, font, top=Decimal("33.6'), margin_left=Decimal('2.5"))
            self.write_word(date, font, top=Decimal("35.3'), margin_left=Decimal('2.5"))

    def certificate_draw(self):
        self.draw.rectangle((round(Decimal("25.3") * self.MULTIPLE), round(Decimal("32.8") * self.MULTIPLE),
                        round(Decimal("30.5") * self.MULTIPLE), (round(Decimal("36") * self.MULTIPLE))), outline="black",
                       width=round(Decimal("0.07") * self.MULTIPLE))
        font_sytle = self.FONT_STYLE_BUTTOM
        font_szie = self.FONT_SZIE_BUTTOM_RIGHT
        font = ImageFont.truetype(font_sytle, round(font_szie * self.MULTIPLE))
        self.write_word('合格证', font, top=Decimal("33.2'), margin_right=Decimal('4.35"))
        self.write_word('已检验', font, top=Decimal("34.5'), margin_right=Decimal('4.35"))

    def print_(self, odoo, input_raw=None):
        if not input_raw:
            return
        response = odoo.env['wizard.mrp.commodity.barcode'].print_commodity_barcode(input_raw)
        if not response:
            return
        if response.get('state') != 0:
            return
        data = response.get('printcontent')
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.name_draw(data.get('first_name'), data.get('second_name'))
        self.color_draw(data.get('color'))
        self.sn_draw(data.get('sn'))
        self.sn_sku_draw(data.get('sn'), data.get('SKU'))
        self.barcode_draw(data.get('barcode'))
        self.address_date_draw(data.get('address'), data.get('datetime'))
        self.certificate_draw()
        TIMES = Decimal("0.4")
        heigh = round(400*TIMES)
        width = round(338*TIMES)
        x1 = 0
        y1 = 0
        x2 = x1+width
        y2 = y1+heigh
        image = QPixmap()
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        image.loadFromData(tmp.getvalue())  # 使用QImage构造图片
        painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()  # 打印结束


