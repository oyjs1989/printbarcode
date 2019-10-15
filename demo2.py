#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo2
#   Author :        lumi
#   date：          2019/10/15
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package

# import clr
# clr.FindAssembly("LabelPainter_SDK.dll")
# clr.FindAssembly("hasp_windows_82155.dll")
# from hasp_windows_82155 import *  # 导入命名空间
# from LabelPainter_SDK import *  # 导入命名空间

# instance = ZL_Initialization(r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\中琅条码标签打印软件')

# lib = ctypes.cdll.LoadLibrary('./LabelPainter_SDK.dll')

import ctypes
# program_path = ctypes.c_char_p("C:\\Program Files (x86)\\中琅条码标签打印软件\\")
program_path = "C:\\Program Files (x86)\\中琅条码标签打印软件\\"
demo_path = r"D:\git_repertory\pythonDemo\qt_demo\barcode\demo1.zhl"

dll = ctypes.windll.LoadLibrary(r"D:\git_repertory\pythonDemo\qt_demo\barcode\LabelPainter_SDK.dll")
# dll.ZL_Initialization.argtypes = [ctypes.POINTER(ctypes.c_char)]
# dll.ZL_Initialization.restype = ctypes.c_char_p
s = dll.ZL_Initialization(program_path)
print(s)
# dll.ZL_OpenDoc(demo_path, "")
# dll.ZL_OutputToPrinter()
# dll.ZL_SetDataCustom()
# dll.ZL_StartOutputCustom()
# dll.ZL_StopOutput()
# dll.ZL_CloseDoc()
# dll.ZL_Release()
