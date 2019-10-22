#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     import_font
#   Author :        lumi
#   date：          2019/10/22
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import win32api
import win32con
import ctypes


ctypes.windll.gdi32.AddFontResourceA("./方正兰亭黑_GBK.TTF")
win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)
