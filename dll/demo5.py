#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo5
#   Author :        lumi
#   date：          2019/10/15
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package



# lib = ctypes.cdll.LoadLibrary('./LabelPainter_SDK.dll')

import ctypes
# program_path = ctypes.c_char_p("C:\\Program Files (x86)\\中琅条码标签打印软件\\")
program_path = "D:\\printer\\"
demo_path = r"D:\git_repertory\pythonDemo\qt_demo\barcode\demo1.zhl"

dll = ctypes.windll.LoadLibrary(r"D:\git_repertory\pythonDemo\qt_demo\barcode\LabelPainter_SDK.dll")
# dll = ctypes.cdll.LoadLibrary(r"D:\git_repertory\pythonDemo\qt_demo\barcode\LabelPainter_SDK.dll")
s = dll.ZL_Initialization(program_path)
print(s)
# dll.ZL_OpenDoc(demo_path, "")
# dll.ZL_OutputToPrinter()
# dll.ZL_SetDataCustom()
# dll.ZL_StartOutputCustom()
# dll.ZL_StopOutput()
# dll.ZL_CloseDoc()
# dll.ZL_Release()