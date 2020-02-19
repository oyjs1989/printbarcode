#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo8_print_pdf
#   Author :        lumi
#   date：          2020/1/13
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import tempfile
import win32api
import win32print


def printer_loading(filename):
    win32api.ShellExecute(0, "printto", filename, '"%s"' % win32print.GetDefaultPrinter(), ".", 0)


import os

path = r'D:\git_repertory\pythonDemo\qt_demo\barcode\print_demo'
for a, b, c in os.walk(path):
    print(c)
# for i in c:
    # f = os.path.join(path, i)
    # printer_loading(f)
f = os.path.join(path, '【需求】为产品类别添加默认损耗率v1.2.pdf')
printer_loading(f)