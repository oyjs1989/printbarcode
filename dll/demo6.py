#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo6
#   Author :        lumi
#   date：          2019/10/15
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
from PIL import Image, ImageDraw
from myqrcode import QrcodeGenerate

width = 2530
height = 2580
barcode_width = 1280
barcode_height = 1280
x, y = 450, 20
im = Image.new('L', (round(width), round(height)), 255)
qr = QrcodeGenerate('G$M:65766$S:326S00005678$D:100982743%Z$Al0123456789ABCDEF$I:023047432043AF3456FEB234524234234567',
                    'Q')
image = qr.get_pilimage(10)
new_image = image.resize((round(barcode_width), round(barcode_height)), Image.ANTIALIAS)
box = (x, y, x + barcode_width, y + barcode_height)
im.paste(new_image, box)
ImageDraw.Draw(im)
im.save('haha.jpg')
