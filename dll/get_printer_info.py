#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     get_printer_info
#   Author :        lumi
#   date：          2019/10/23
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import win32print
import win32ui
from decimal import *

printer_name = win32print.GetDefaultPrinter()
times = Decimal('2.54')
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

#
# You can only write a Device-independent bitmap
#  directly to a Windows device context; therefore
#  we need (for ease) to use the Python Imaging
#  Library to manipulate the image.
#
# Create a device context from a named printer
#  and assess the printable size of the paper.
#
hDC = win32ui.CreateDC()
hDC.CreatePrinterDC(printer_name)
printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)  # 可打印的物理长宽
printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)  # 物理总长宽  = 可打印的物理长宽+物理偏移
printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)  # 物理偏移

print(printable_area, printer_size, printer_margins)
print(hDC.GetDeviceCaps(LOGPIXELSX), hDC.GetDeviceCaps(LOGPIXELSY))
print(Decimal(hDC.GetDeviceCaps(HORZRES)) / Decimal(hDC.GetDeviceCaps(LOGPIXELSX)) * times,
      Decimal(hDC.GetDeviceCaps(VERTRES)) / Decimal(hDC.GetDeviceCaps(LOGPIXELSY)) * times)
