#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     prroundimage
#   Author :        lumi
#   date：          2019/9/20
#   Description :
'''
# - Custom package
from decimal import *
# - Third party module of python

# - import odoo package
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageWin
import win32print
import win32ui
import win32con
import win32gui
from mycode128 import Code128Generate
from myean13 import EAN13Generate
import os

def get_font_path(file_path):
    if os.path.isfile(file_path):
        return file_path
    try:
        ImageFont.truetype(file_path,10)
        return file_path
    except Exception as e:
        raise Exception('%s not found'%file_path)
# HORZRES / VERTRES = printable area
#
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
PHYSICALOFFSETX = 0
PHYSICALOFFSETY = 0

HORZSIZE = 25.4 * HORZRES/LOGPIXELSX



# print size
TIMES = 2.5
PRINT_WIDTH = round(338*TIMES)
PRINT_HEIGHT = round(400*TIMES)

printer_name = win32print.GetDefaultPrinter()
p = win32print.OpenPrinter(printer_name)

def print_image(image):
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
    printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
    printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)
    # print(printable_area)
    # print(printer_size)
    # print(printer_margins)
    if image.size[0] > image.size[1]:
        image = image.rotate(90)
    ratios = [1.0 * printable_area[0] / image.size[0], 1.0 * printable_area[1] / image.size[1]]
    scale = min(ratios)

    # Start the print job, and draw the bitmap to
    #  the printer device at the scaled size.

    hDC.StartDoc(file_name)
    hDC.StartPage()
    scaled_width, scaled_height = PRINT_WIDTH, PRINT_HEIGHT
    image = image.resize((scaled_width, scaled_height))
    dib = ImageWin.Dib(image)
    print(printer_margins)
    print(printer_size)
    print(printable_area)
    # scaled_width, scaled_height = [int(scale * i) for i in image.size]
    x1 = int((printer_size[0] - scaled_width) / 2)
    y1 = int((printer_size[1] - scaled_height) / 2)
    y1 = 0
    x1=0
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
    # x1, x2, y1, y2 = 700, 1500, 330, 1800

    # dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))
    #
    # hDC.EndPage()
    # hDC.EndDoc()
    # hDC.DeleteDC()


# 1in = 2.54cm = 25.4 mm = 72pt = 6pc
MULTIPLE = Decimal('50')
width = MULTIPLE * Decimal('33.8')
height = MULTIPLE * Decimal('40.0')
PT_TO_MM_DECIMAL = Decimal('25.4') / Decimal('72')

FONT_STYLE_HEAD = get_font_path('方正兰亭黑_GBK.TTF')
FONT_SZIE_HEAD = Decimal('4') * PT_TO_MM_DECIMAL

# FONT_STYLE_MID = 'ArialRegular.ttf'
FONT_STYLE_MID = get_font_path('Arial.ttf')
FONT_SZIE_MID = Decimal('4.5') * PT_TO_MM_DECIMAL

FONT_STYLE_CODE = get_font_path('Arial Unicode MS.TTF')
FONT_SZIE_CODE = Decimal('10') * PT_TO_MM_DECIMAL

FONT_STYLE_BUTTOM = get_font_path('方正兰亭黑.TTF')
FONT_SZIE_BUTTOM_LIFT = Decimal('4') * PT_TO_MM_DECIMAL
FONT_SZIE_BUTTOM_RIGHT = Decimal('3.18') * PT_TO_MM_DECIMAL


file_name = 'code.jpg'

image = Image.new('L', (round(width), round(height)), 255)
draw = ImageDraw.Draw(image)



def write_word(words, font, top=0, margin_left=0, margin_right=0):
    y = top * MULTIPLE
    text_width, text_height = font.getsize(words)
    if margin_left:
        x = margin_left * MULTIPLE
    elif margin_right:
        x = width - margin_right * MULTIPLE - text_width
    else:
        x = 0
    draw.text((round(x), y), words, font=font, fill=0)
    return Decimal(text_height) / MULTIPLE


def name_draw(first_name, second_name):
    first_name_y = Decimal('3')
    font_sytle = FONT_STYLE_HEAD
    font_szie = FONT_SZIE_HEAD
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    text_width, text_height = font.getsize(first_name)
    write_word(first_name, font, top=first_name_y, margin_left=3)
    second_name_y = first_name_y + Decimal(text_height)/MULTIPLE
    write_word(second_name, font, top=second_name_y, margin_left=3)


def color_draw(color):
    font_sytle = FONT_STYLE_HEAD
    font_szie = FONT_SZIE_HEAD
    color_y = Decimal('3')
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    write_word(color, font, top=color_y, margin_right=3)


def sn_draw(sn):
    cd = Code128Generate(sn, image, options={'MULTIPLE': MULTIPLE})
    barcode_width = Decimal('27.8') * MULTIPLE
    barcode_height = Decimal('5') * MULTIPLE
    x = Decimal('3') * MULTIPLE
    y = Decimal('6.5') * MULTIPLE
    box = (x, y, x + barcode_width, y + barcode_height)
    im = cd.get_pilimage(barcode_width, barcode_height)
    im.save('sss.jpg')
    image.paste(im, box)


def sn_sku_draw(sn, sku):
    font_sytle = FONT_STYLE_MID
    font_szie = FONT_SZIE_MID
    y = Decimal('11.7')
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    write_word(sn, font, top=y, margin_left=3)
    write_word(sku, font, top=y, margin_right=3)


def barcode_draw(barcode):
    font_sytle = FONT_STYLE_CODE
    font_szie = FONT_SZIE_CODE
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    cd = EAN13Generate(barcode, image, font, options={'MULTIPLE': MULTIPLE})
    barcode_width = Decimal('27.8') * MULTIPLE
    barcode_height = Decimal('21') * MULTIPLE
    x = Decimal('3') * MULTIPLE
    y = Decimal('14.1') * MULTIPLE
    box = (x, y, x + barcode_width, y + barcode_height)
    im = cd.get_pilimage(barcode_width, barcode_height)
    image.paste(im, box)


def address_date_draw(address, date):
    font_sytle = FONT_STYLE_BUTTOM
    font_szie = FONT_SZIE_BUTTOM_LIFT
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    write_word(address, font, top=Decimal('33.6'), margin_left=3)
    write_word(date, font, top=Decimal('35.1'), margin_left=3)


def certificate_draw():
    draw.rectangle((round(Decimal('25') * MULTIPLE), round(Decimal('33.89') * MULTIPLE),
                    round(Decimal('30.8') * MULTIPLE), (round(Decimal('37') * MULTIPLE))), outline="black",
                   width=round(Decimal('0.07') * MULTIPLE))
    font_sytle = FONT_STYLE_BUTTOM
    font_szie = FONT_SZIE_BUTTOM_RIGHT
    font = ImageFont.truetype(font_sytle, round(font_szie * MULTIPLE))
    write_word('合格证', font, top=Decimal('34.2'), margin_right=Decimal('4.25'))
    write_word('已检验', font, top=Decimal('35.5'), margin_right=Decimal('4.25'))


name_draw(u'小米米家智能门锁', u'颜色:碳素黑')
color_draw('颜色:碳素黑')
sn_draw('25311/99999999')
sn_sku_draw('25311/99999999', 'SKU:SZB4022CN')
barcode_draw('6934177714108')
address_date_draw('生产地址:广东省佛山市南海区', '生产日期:2019.09')
certificate_draw()
image.save(file_name, 'jpeg')

print_image(image)