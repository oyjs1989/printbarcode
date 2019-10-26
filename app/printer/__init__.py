#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     __init__.py
#   Author :        lumi
#   date：          2019/10/24
#   Description :
'''
# - Custom package
from io import BytesIO
from decimal import *
import win32print
import win32ui
from PIL import Image, ImageWin

# Inches to centimeters
INC_TO_CM = Decimal('2.54')

# HORZRES / VERTRES = printable area

HORZRES = 8
VERTRES = 10
#
# LOGPIXELS = dots per inch
#
LOGPIXELSX = 88
LOGPIXELSY = 90
#
# PHYSICALWIDTH/HEIGHT = total area
#
PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111
#
# PHYSICALOFFSETX/Y = left / top margin
#
PHYSICALOFFSETX = 112
PHYSICALOFFSETY = 113

printer_name = win32print.GetDefaultPrinter()
hDC = win32ui.CreateDC()
hDC.CreatePrinterDC(printer_name)
printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)  # 可打印的物理长宽
printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)  # 物理总长宽  = 可打印的物理长宽+物理偏移
printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)  # 物理偏移

print(printable_area, printer_size, printer_margins)
print(hDC.GetDeviceCaps(LOGPIXELSX), hDC.GetDeviceCaps(LOGPIXELSY))
print(Decimal(hDC.GetDeviceCaps(HORZRES)) / Decimal(hDC.GetDeviceCaps(LOGPIXELSX)) * INC_TO_CM,
      Decimal(hDC.GetDeviceCaps(VERTRES)) / Decimal(hDC.GetDeviceCaps(LOGPIXELSY)) * INC_TO_CM)

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
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        self.font_style = get_font_path('./Fonts/Arial.ttf')
        self.virtual_multiple = Decimal("100")  #  虚拟图像放大倍数
        self.virtual_width = self.virtual_multiple * Decimal("25.3")
        self.virtual_height = self.virtual_multiple * Decimal("25.8")
        self.reality_multiple = Decimal("3.78")  # 打印机放大倍数
        self.reality_heigh = round(Decimal('25.8') * self.reality_multiple)
        self.reality_width = round(Decimal('25.4') * self.reality_multiple)
        self.image = Image.new('L', (round(self.virtual_width), round(self.virtual_height)), 255)
        self.draw = ImageDraw.Draw(self.image)

    def printbarcode(self):
        x1 = 0
        y1 = 0
        x2 = x1 + self.reality_width
        y2 = y1 + self.reality_heigh
        tmp = BytesIO()
        self.image.save(tmp, format='BMP')
        image = QPixmap()
        image.loadFromData(tmp.getvalue())                # 使用QImage构造图片
        painter = QPainter(self.print_device)             # 使用打印机作为绘制设备
        painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        painter.end()                                     # 打印结束

    def prv(self):
        pass

    def after(self):
        pass

    def run(self):
        self.prv()
        self.printbarcode()
        self.after()

class NetPrinter(Printer):
    '''互联网信息打印'''

    def get_net_info(self):
        pass

class LocalPrinter(Printer):
    '''
    本地打印，不需要互联网信息
    '''
    pass

