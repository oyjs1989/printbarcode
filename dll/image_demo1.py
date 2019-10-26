#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     image_demo1
#   Author :        lumi
#   date：          2019/10/23
#   Description :
'''
# - Custom package

# - Third party module of python
print(__name__)
# - import odoo package
from PIL import Image, ImageDraw, ImageFont
import textwrap
width = 255
height = 255
im = Image.new('L', (round(width), round(height)), 255)
draw = ImageDraw.Draw(im)
x, y = 100, 100
align = 'right'
align = 'right'
words = '床前明月光，\n疑是地上霜'
font_style = '方正兰亭黑.TTF'
font_style = 'c:/windows/fonts/Arial.ttf'
# lines = textwrap.wrap(words, width=40)
# print(lines)
# font = ImageFont.truetype(font_style, 10)
# draw.text((round(x), y), words, font=font, fill=0, align=align)
# draw.rectangle([10, 20, 40, 30], width=2)
# im.save('text.png')
font = ImageFont.truetype(font_style, 10)
# print(font.getsize_multiline('222222\nasdsadsssssssssssssssssssadsa')) #(152, 24)
# print(font.getsize_multiline('222222\nasdsadsssssssssssssssssssadsa\n')) #(152, 38)
print(font.getsize_multiline('222222\nasdsadsssssssssssssssssssadsan')) #(158, 24)