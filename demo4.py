#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo4
#   Author :        lumi
#   date：          2019/10/9
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package

import clr
import time
clr.FindAssembly(r"D:\git_repertory\pythonDemo\qt_demo\barcode\PrintDll.dll")  ## 加载c#dll文件
from PrintDll import *  # 导入命名空间
instance = Print()
instance.PrintBarcode('123456789123', r'C:\Program Files (x86)\Seagull\BarTender Suite', r'C:\Users\lumi\Desktop', 'demo.btw')  # class1是dll里面的类
time.sleep(10)


instance.PrintBarcode('123456789123', r'C:\Program Files (x86)\Seagull\BarTender Suite', r'C:\Users\lumi\Desktop', 'demo.btw')  # class1是dll里面的类
# instance.PrintBarcode('123456789123', r'C:\Program Files (x86)\Seagull\BarTender Suite', r'C:\Users\lumi\Desktop', 'demo.btw')  # class1是dll里面的类
