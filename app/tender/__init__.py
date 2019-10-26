#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     __init__.py
#   Author :        lumi
#   date：          2019/10/24
#   Description :
'''

if __name__ == '__main__':
    MODE = 'debug'
else:
    MODE = 'produce'

from decimal import *
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from mycode128 import Code128Generate
from myean13 import EAN13Generate
from myqrcode import QrcodeGenerate

BARCODE = {
    'code128': Code128Generate,
    'ean13': EAN13Generate,
    'qrcode': QrcodeGenerate,
}

DEFAULT_MULTIPLE = Decimal('50')
OBJ_REFERENCE_POINT = {
    'LEFT_TOP': (0, 0),
    'RIGHT_TOP': (2, 0),
    'CENTER_TOP': (1, 0),
    'LEFT_MID': (0, 1),
    'RIGHT_MID': (2, 1),
    'CENTER_MID': (1, 1),
    'LEFT_BOTTOM': (0, 2),
    'RIGHT_BOTTOM': (2, 2),
    'CENTER_BOTTOM': (1, 2)}

TMP_REFERENCE_POINT = {
    'LEFT_TOP': (0, 0),
    'RIGHT_TOP': (2, 0),
    'CENTER_TOP': (1, 0),
    'LEFT_MID': (0, 1),
    'RIGHT_MID': (2, 1),
    'CENTER_MID': (1, 1),
    'LEFT_BOTTOM': (0, 2),
    'RIGHT_BOTTOM': (2, 2),
    'CENTER_BOTTOM': (1, 2)}


class BaseTender(object):

    def __init__(self, image, draw, width=0, height=0, x=0, y=0, obj_reference_point=OBJ_REFERENCE_POINT['LEFT_TOP'],
                 tmp_reference_point=TMP_REFERENCE_POINT['LEFT_TOP'], horizontal_center=False, vertical_center=False,
                 multiple=DEFAULT_MULTIPLE, rotate=0, **kwargs):
        self.image = image
        self.draw = draw
        self.x = Decimal(x) * multiple
        self.y = Decimal(y) * multiple
        self.width = Decimal(width) * multiple
        self.height = Decimal(height) * multiple
        self.horizontal_center = horizontal_center  # 水平居中为高级选项，固定为水平居中
        self.vertical_center = vertical_center  # 垂直居中为高级选项，固定为垂直居中
        self.obj_reference_point = obj_reference_point
        self.tmp_reference_point = tmp_reference_point
        self.multiple = multiple
        self.rotate = rotate
        self.characteristic = kwargs

    def verify_width_height(self):
        '''
        1.计算长宽（二维码，条码，文本）   输入的值（非图形类）
        如果文本长度少于  width 则已为本长度为准
        如果文本长度高于 width  则换行已width为准
        如果
        :return:
        '''
        pass

    def calculation_absolute_position(self):
        '''根据目标点，对照点 xy 计算绝对位置'''
        pass

    def calculation_relative_position(self):
        '''
        计算左上角的位置  PIL固定位置
        :return:
        '''
        pass

    def calculation_position(self):
        # 先计算长宽
        self.verify_width_height()
        # 计算相对位置
        self.calculation_relative_position()
        # 计算绝对位置
        self.calculation_absolute_position()

    def prev(self, context):
        self.context = context
        self.calculation_position()

    def after(self):
        pass

    def drawing(self):
        pass

    def run(self, context):
        # 布局
        self.prev(context)
        # 打印
        self.drawing()
        # 收尾
        self.after()


class TextTender(BaseTender):
    '''文本打印'''

    def __init__(self, *arg, **kwargs):
        super(TextTender, self).__init__(*arg, **kwargs)
        self.font_size = Decimal(self.characteristic.get('font_size'))
        self.font_style = self.characteristic.get('font_style')
        self.direction = self.characteristic.get('direction')  # direction: 文字的書寫方向rtl 從右開始寫到左邊 ltr 從左邊到右邊 ttb 從上到下
        self.spacing = self.characteristic.get('spacing')  # 行距
        self.align = self.characteristic.get('align')  # align: 設定文字的對齊方式，left/center/right 主要针对有换行数据，因为长短不一
        self.font = ImageFont.truetype(self.font_style, round(self.font_size * self.multiple))

    def drawing(self):
        self.draw.text((round(self.x), round(self.y)), self.context, font=self.font, fill=0)


class MultilineTender(TextTender):
    '''多行文本,高度是动态的 单行'''

    def verify_width_height(self):
        '''
        处理对行文本
        :return:
        '''
        self.multi_spilt()

    def multi_spilt(self):
        '''
        多行文本根据宽度换行，并重新计算长宽
        :return:
        '''
        new_context = ''
        line = ''
        total_height = 0
        for w in self.context:
            text_width, text_height = self.font.getsize(line)
            if text_width > self.width:
                new_context += line[0:-1]
                new_context += '\n'
                line = w
                total_height += text_height
            else:
                line += w
        self.context = new_context
        self.width, self.height = self.font.getsize_multiline(new_context)


class BarcodeTender(BaseTender):
    '''
    二维码/条码打印
    '''

    def __init__(self, *arg, **kwargs):
        super(BarcodeTender, self).__init__(*arg,**kwargs)
        self.barcode_type = self.characteristic.get('barcode_type')
        self.font_style = self.characteristic.get('font_style')
        self.font = ImageFont.truetype(self.font_style, round(self.font_size * self.multiple))


class PictureTender(BaseTender):
    '''
    嵌入图片
    '''

    def __init__(self, *arg, **kwargs):
        super(PictureTender, self).__init__(*arg, **kwargs)
        self.image_path = self.characteristic.get('image_path')


class ImagesTender(BaseTender):
    '''
    绘图
    '''

    def __init__(self, *arg, **kwargs):
        super(ImagesTender, self).__init__(*arg, **kwargs)
        self.shape = self.characteristic.get('shape')
        self.thickness = self.characteristic.get('thickness')


TENDERS = {
    'singleline': TextTender,
    'multiline': MultilineTender,
    'pic': PictureTender,
    'img': ImagesTender,
    'barcode': BarcodeTender,
}


class BackGround(object):

    def __init__(self, width, height, components, multiple=DEFAULT_MULTIPLE):
        '''
        一个背景应该拥有：
        1.长宽 2 背景色 内部内容 绘制图片功能
        '''
        self.width = width * multiple
        self.height = height * multiple
        self.image = Image.new('L', (round(self.width), round(self.height)), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.components = self.after_init(multiple, components)

    def after_init(self, multiple, components):
        '''
        生成所有的部件对象
        :param multiple:
        :param components:
        :return:
        '''
        result = {}
        for component in components:
            component_type = component.get('type')
            component_name = component.get('name')
            if component_type not in TENDERS:
                raise Exception('%s类型type不存在')
            result[component_name] = TENDERS[component_type](self.image, self.draw, **component, multiple=multiple)
        return result

    def drawing(self, contexts):
        for name, obj in self.components.items():
            obj.run(contexts.get(name))
        tmp = BytesIO()
        if MODE == 'debug':
            self.image.save('debug.png', format='BMP')
        self.image.save(tmp, format='BMP')
        return tmp.getvalue()


if __name__ == '__main__':
    kwargs = {
        'width': 20,
        'height': 20,
        'components': [
            {
                'type': 'singleline',
                'x': 2,
                'y': 2,
                'height': 3,
                'width': 3,
                'name': '字段1',
                'font_style': 'Arial.ttf',
                'font_size': 4.5,
            }
        ]
    }
    bg = BackGround(**kwargs)
    bg.drawing({'字段1': 'haha'})
