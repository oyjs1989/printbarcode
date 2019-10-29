"""Rendering code for EAN-13 barcode"""

from functools import reduce
from io import BytesIO
from decimal import *
from PIL import Image, ImageFont, ImageDraw

# maps bar width against font size
font_sizes = {
    1: 8,
    2: 14,
    3: 18,
    4: 24
}


class EAN13Renderer:
    """Rendering class - given the code and corresponding
    bar encodings and guard bars,
    it will add edge zones and render to an image"""

    width = None
    height = None

    def __init__(self, code, left_bars, right_bars, guards, font, img, options):
        self.code = code
        self.left_bars = left_bars
        self.right_bars = right_bars
        self.guards = guards
        self.font = font
        self.img = img
        self.options = options
        self.set_args()

    def set_args(self):
        def sum_len(total, item):
            """add the length of a given item to the total"""
            return total + len(item)

        num_bars = (7 * 12) + reduce(sum_len, self.guards, 0)
        MULTIPLE = self.options.get('MULTIPLE')
        self.image_width = self.options.get('width', Decimal('0')) * MULTIPLE or self.img.width - self.margin_left - self.margin_right
        if self.img.width < self.margin_left + self.margin_right + self.image_width:
            self.image_width = self.img.size[1] - self.margin_left - self.margin_right

        self.image_height = self.options.get('height', Decimal('0')) * MULTIPLE or self.img.height - self.margin_top - self.margin_bottom
        if self.img.height < self.margin_top + self.margin_bottom + self.image_height:
            self.image_height = self.img.height - self.margin_top - self.margin_bottom
        width, height = self.font.getsize(self.code[0])
        self.bar_width = round((self.image_width - width) / num_bars)
        self.current = self.margin_top + self.margin_bottom + self.image_height

    def write_image(self):
        bar_width = self.bar_width
        img = self.img
        bar_height = self.image_height
        margin_left = self.margin_left
        margin_top = self.margin_top
        width, height = self.font.getsize(self.code[0])

        class BarWriter:
            """Class which moves across the image, writing out bars"""

            def __init__(self, img):
                self.img = img
                self.current_x = margin_left + width
                self.symbol_top = margin_top
                self.bar_height = bar_height

            def write_bar(self, value, full=False):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                bar_height = round(self.bar_height * Decimal(full and 0.88 or 0.8))
                if value == 1:
                    for ypos in range(round(self.symbol_top), round(bar_height + self.symbol_top)):
                        for xpos in range(round(self.current_x),
                                          round(self.current_x + bar_width)):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars, full=False):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar), full)

        # Draw the bars
        writer = BarWriter(self.img)
        writer.write_bars(self.guards[0], full=True)
        writer.write_bars(self.left_bars)
        writer.write_bars(self.guards[1], full=True)
        writer.write_bars(self.right_bars)
        writer.write_bars(self.guards[2], full=True)
        # Draw the text
        draw = ImageDraw.Draw(self.img)
        draw.text((margin_left, round(margin_top + bar_height * Decimal(0.75))), self.code[0], font=self.font)
        draw.text((21 * bar_width, round(margin_top + bar_height * Decimal(0.75))), self.code[1:7], font=self.font)
        draw.text((67 * bar_width, round(margin_top + bar_height * Decimal(0.75))), self.code[7:], font=self.font)

    def get_pilimage(self, barcode_width, barcode_height, bar_width):
        def sum_len(total, item):
            """add the length of a given item to the total"""
            return total + len(item)

        width, height = self.font.getsize(self.code[0])
        num_bars = (7 * 12) + reduce(sum_len, self.guards, 0)

        image_width = num_bars * bar_width
        font_width = round(width / barcode_width * image_width)
        image_width = round(width / barcode_width * image_width + image_width)
        image_height = round(image_width / barcode_width * barcode_height)

        img = Image.new('L', (image_width, image_height), 255)

        class BarWriter:
            """Class which moves across the image, writing out bars"""

            def __init__(self, img):
                self.img = img
                self.current_x = font_width
                self.symbol_top = 0

            def write_bar(self, value, full=False):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                bar_height = int(image_height * (full and 0.9 or 0.8))
                if value == 1:
                    for ypos in range(self.symbol_top, bar_height):
                        for xpos in range(self.current_x, self.current_x + bar_width):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars, full=False):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar), full)

        # Draw the bars
        writer = BarWriter(img)
        writer.write_bars(self.guards[0], full=True)
        writer.write_bars(self.left_bars)
        writer.write_bars(self.guards[1], full=True)
        writer.write_bars(self.right_bars)
        writer.write_bars(self.guards[2], full=True)

        # to set new pix
        img = img.resize((round(barcode_width), round(barcode_height)))

        # Draw the text
        draw = ImageDraw.Draw(img)
        draw.text((Decimal(0.0) * barcode_width, round(barcode_height * Decimal(0.75))), self.code[0], font=self.font)
        draw.text((Decimal(0.095) * barcode_width, round(barcode_height * Decimal(0.75))), self.code[1:7], font=self.font)
        draw.text((Decimal(0.55) * barcode_width, round(barcode_height * Decimal(0.75))), self.code[7:], font=self.font)
        return img
