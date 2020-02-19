#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     qrcodegenerate
#   Author :        lumi
#   date：          2019/10/15
#   Description :
'''
# - Custom package

# - Third party module of python

try:
    from .textencoder import TextEncoder
    from .renderer import QRCodeRenderer
except ImportError:
    from textencoder import TextEncoder
    from renderer import QRCodeRenderer
try:
    from PIL import Image
except ImportError:
    import Image

class QrcodeGenerate(object):
    """Top-level class which handles the overall process of
        encoding input data, placing it in the matrix and
        outputting the result"""

    def __init__(self, text, ecl=None, **option):
        '''
        ecl 是纠错等级相关，可选如下：
        ErrorCorrectionLevel.L
        ErrorCorrectionLevel.M
        ErrorCorrectionLevel.Q
        ErrorCorrectionLevel.H
        :param text:
        :param ecl:
        '''
        """Set up the encoder with the input text.
        This will encode the text,
        and create a matrix with the resulting codewords"""

        enc = TextEncoder()
        self.matrix = enc.encode(text, ecl)
        self.height = 0
        self.width = 0
        self.option = option

    def save(self, filename, cellsize=5):
        """Write the matrix out to an image file"""

        qrc = QRCodeRenderer(self.matrix)
        qrc.write_file(cellsize, filename)

    def get_imagedata(self, cellsize=5):
        """Write the matrix out to a PNG bytestream"""

        qrc = QRCodeRenderer(self.matrix)
        imagedata = qrc.get_imagedata(cellsize)
        self.height = qrc.mtx_size
        self.width = qrc.mtx_size
        return imagedata

    def get_ascii(self):
        """Return an ascii representation of the matrix"""
        qrc = QRCodeRenderer(self.matrix)
        return qrc.get_ascii()

    def get_pilimage(self, cellsize=5, colour=0, width=4):
        qrc = QRCodeRenderer(self.matrix)
        return qrc.get_pilimage(cellsize, colour=colour, width=width)


if __name__ == '__main__':
    s = 'G$M:1694$S:456SS111992900009$D:000000000F358D05%Z$A:04CF8CDF3C765017$I:163AF41829724ED328243F8A91C5179CC548'
    qr = QrcodeGenerate(s, 'l')
    image = qr.get_pilimage(10, width=0)
    image.save('qrcode.png','png')