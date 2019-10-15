#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     demo1
#   Author :        lumi
#   date：          2019/10/14
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import clr
clr.FindAssembly("PrintDll.dll")  ## 加载c#dll文件
from PrintDll import *  # 导入命名空间

instance = Print()
# instance.PrintBarcode('小米米家智能门锁,标准锁体 40~80mm门厚,颜色：碳素黑,21379/00048293,SKU:SZB4022CN,6934177714108,生产地址：广东省佛山市南海区,生产日期：2019.09', r'C:/Program Files (x86)/Seagull/BarTender Suite', r'D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model' ,'米家69码打印.btw')
# instance.PrintBarcode('智能门锁,标准锁体 40~80mm门厚,颜色：碳素黑,456/S111992599998,SKU:ADO006CNB01,6934177714108,生产地址：广东省佛山市南海区,生产日期：2019.09', r'C:/Program Files (x86)/Seagull/BarTender Suite', r'D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model' ,'aqara69码打印.btw')
# instance.PrintBarcode('aaaaaaaaaa', r'C:/Program Files (x86)/Seagull/BarTender Suite', r'D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model' ,'demo.btw')



# import clr
# clr.FindAssembly("Seagull.BarTender.Print.dll")  ## 加载c#dll文件
# from Seagull.BarTender.Print import *  # 导入命名空间
#
# instance = Engine()
# instance.Start()
# btFormat = instance.Documents.Open(r"D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model\demo.btw")
# print(btFormat.SubStrings)
# btFormat.SubStrings["title"].Value = 'asdsadasd'
# btFormat.SubStrings["barcode"].Value = '123456789123'
# # instance.PrintBarcsadsaode('asdsadasd,123456789123,asdsadasd', r'C:/Program Files (x86)/Seagull/BarTender Suite', r'D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model' ,'demo.btw')
# # instance.PrintBarcode('aaaaaaaaaa', r'C:/Program Files (x86)/Seagull/BarTender Suite', r'D:\git_repertory\pythonDemo\qt_demo\barcode\barcode_model' ,'demo.btw')
# #指定印表機名
# btFormat.PrintSetup.PrinterName = "Postek G6000"
# #改變標籤列印數份連載
# btFormat.PrintSetup.NumberOfSerializedLabels = 1
# #列印份數
# btFormat.PrintSetup.IdenticalCopiesOfLabel = 1
# waitout = 10000
# nResult1 = btFormat.Print("标签打印软件", waitout, None)
# btFormat.PrintSetup.Cache.FlushInterval = CacheFlushInterval.PerSession
# instance.Stop();
