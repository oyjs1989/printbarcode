# -*- coding:utf-8 -*-
from decimal import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QSizeF,QRect,Qt,QSize
from PyQt5.QtWebChannel import QWebChannel
# from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtGui import QPainter, QImage,QPagedPaintDevice,QPixmap
import sys, base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageWin

class Printer:
    def __init__(self):
        self.p = QPrinterInfo.defaultPrinter()
        self.print_device = QPrinter(self.p)
        # self.print_device.setPaperSize(QSizeF(400, 338), QPrinter.Point) #设置打印机数据

    def print_(self, data=None):
        TIMES = Decimal('0.4')
        # image_data = open('./code.jpg', 'rb').read()
        # image_content = base64.b64decode(data_url)  # 数据流base64解码
        # image = QImage()
        heigh = round(400*TIMES)
        width = round(338*TIMES)
        x1 = 0
        y1 = 0
        x2 = x1+width
        y2 = y1+heigh
        image = QPixmap()
        im = Image.open('./new.jpg')
        print(im.tobytes())
        print(open('./new.jpg','rb').read())
        # image.load('./code.jpg')
        # image = image.scaled(QSize(width, heigh), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # image.loadFromData(open('./new.jpg','rb').read())  # 使用QImage构造图片
        # painter = QPainter(self.print_device)  # 使用打印机作为绘制设备
        # painter.drawImage(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        # painter.drawPixmap(QRect(x1, y1, x2, y2), image)  # 进行绘制（即调起打印服务）
        # painter.end()  # 打印结束


class Print(QObject):
    def __init__(self):
        super().__init__()
        self.printer = Printer()

    @pyqtSlot(str, result=str)
    def print_(self):
        # 去除头部标识
        self.printer.print_()
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # browser = QWebEngineView()
    # browser.setWindowTitle('使用PyQt5打印热敏小票')
    # browser.resize(900, 600)
    # channel = QWebChannel()
    printer = Print()
    printer.print_()
    # channel.registerObject('printer', printer)
    # browser.page().setWebChannel(channel)
    url_string = "file:///python/print/webprint.html"  # 内置的网页地址
    # browser.load(QUrl(url_string))
    # browser.show()
    sys.exit(app.exec_())
