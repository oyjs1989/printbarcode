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
    '''打印'''

    def __init__(self, file_name, image):
        if image.size[0] > image.size[1]:
            image = image.rotate(90)

        ratios = [1.0 * printable_area[0] / image.size[0], 1.0 * printable_area[1] / image.size[1]]
        scale = min(ratios)

        #
        # Start the print job, and draw the bitmap to
        #  the printer device at the scaled size.
        #
        hDC.StartDoc(file_name)
        hDC.StartPage()

        dib = ImageWin.Dib(image)
        scaled_width, scaled_height = [int(scale * i) for i in image.size]
        x1 = int((printer_size[0] - scaled_width) / 2)
        y1 = int((printer_size[1] - scaled_height) / 2)
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()


