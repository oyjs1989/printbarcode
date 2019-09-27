"""Code-128 barcode encoder

All needed by the user is done via the Code128Encoder class:



Implemented by Helen Taylor for HUDORA GmbH.
Updated and ported to Python 3 by Michael Mulqueen for Method B Ltd.

Detailed documentation on the format here:
http://www.barcodeisland.com/code128.phtml
http://www.adams1.com/pub/russadam/128code.html

You may use this under a BSD License.
"""
from .textencoder import TextEncoder
import logging
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from decimal import *

log = logging.getLogger("code128")

# maps bar width against font size
FONT_SIZES = {
    1: 8,
    2: 14,
    3: 18,
    4: 24
}


class Code128Generate:
    """Top-level class which handles the overall process of
    encoding input string and outputting the result"""

    def __init__(self, text, img, options=None):
        """ The options hash currently supports three options:
            * ttf_font: absolute path to a truetype font file used to render the label
            * ttf_fontsize: the size the label is drawn in
            * label_border: number of pixels space between the barcode and the label
            * bottom_border: number of pixels space between the label and the bottom border
            * height: height of the image in pixels """

        self.options = options
        self.text = text
        self.img = img
        encoder = TextEncoder()

        self.encoded_text = encoder.encode(self.text)
        log.debug("Encoded text is %s", self.encoded_text)

        self.checksum = self.calculate_check_sum()
        log.debug("Checksum is %d", self.checksum)

        self.bars = encoder.get_bars(self.encoded_text, self.checksum)
        log.debug("Bars: %s", self.bars)

    def calculate_check_sum(self):
        """Calculate the check sum of the encoded text.
        Checksum is based on the input text and the starting code,
        and a mod103 algorithm is used"""

        checksum = self.encoded_text[0]

        for index, char in enumerate(self.encoded_text):
            if index > 0:
                checksum += (index * char)

        return checksum % 103

    def write_image(self):
        """Write the matrix out to an PNG bytestream"""

        barcode = Code128Renderer(self.bars, self.text, self.img, self.options)
        imagedata = barcode.write_image()
        return imagedata

    def get_pilimage(self, barcode_width, barcode_height, bar_width=4):
        """Write the matrix out to an PNG bytestream"""

        barcode = Code128Renderer(self.bars, self.text, self.img, self.options)
        image = barcode.get_pilimage(barcode_width, barcode_height, bar_width)
        return image


class Code128Renderer:
    """Rendering class for code128 - given the bars and the original
    text, it will render an image of the barcode, including edge
    zones and text."""

    def __init__(self, bars, text, img, options=None):
        """ The options hash currently supports three options:
            * ttf_font: absolute path to a truetype font file used to render the label
            * ttf_fontsize: the size the label is drawn in
            * label_border: number of pixels space between the barcode and the label
            * bottom_border: number of pixels space between the label and the bottom border
            * height: height of the image in pixels
            * show_label: whether to show the label below the barcode (defaults to True) """
        self.options = options or {}
        self.bars = bars
        self.text = text
        self.img = img
        self.set_args()

    def set_args(self):
        MULTIPLE = self.options.get('MULTIPLE')
        self.margin_left = self.options.get('margin_left', Decimal('0')) * MULTIPLE
        self.margin_right = self.options.get('margin_right', Decimal('0')) * MULTIPLE
        if self.margin_left + self.margin_right > self.img.size[1]:
            raise OverflowError('margin left and margin right over width in total')

        self.margin_top = self.options.get('margin_top', Decimal('0')) * MULTIPLE
        self.margin_bottom = self.options.get('margin_bottom', Decimal('0')) * MULTIPLE
        if self.margin_top + self.margin_bottom > self.img.height:
            raise OverflowError('margin top and margin bottom over height in total')

        self.image_width = self.options.get('width', Decimal('0')) * MULTIPLE or self.img.width - self.margin_left - self.margin_right
        if self.img.width < self.margin_left + self.margin_right + self.image_width:
            self.image_width = self.img.size[1] - self.margin_left - self.margin_right

        self.image_height = self.options.get('height', Decimal('0')) * MULTIPLE or self.img.height - self.margin_top - self.margin_bottom
        if self.img.height < self.margin_top + self.margin_bottom + self.image_height:
            self.image_height = self.img.height - self.margin_top - self.margin_bottom
        self.bar_width = int(self.image_width / len(self.bars))
        self.current = self.margin_top + self.margin_bottom + self.image_height

    def write_image(self):
        """Return the barcode as a PIL object"""
        bar_width = self.bar_width
        img = self.img
        bar_height = self.image_height
        margin_left = self.margin_left
        margin_top = self.margin_top

        class BarWriter:
            """Class which moves across the image, writing out bars"""

            def __init__(self, bar_height):
                self.current_x = margin_left
                self.bar_height = bar_height
                self.symbol_top = margin_top

            def write_bar(self, value):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                if value == 1:
                    for ypos in range(round(self.symbol_top), round(self.bar_height + self.symbol_top)):
                        for xpos in range(round(self.current_x), round(self.current_x + bar_width)):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar))

        # draw the barcode bars themselves
        writer = BarWriter(bar_height)
        writer.write_bars(self.bars)
        return self.current

    def get_pilimage(self, barcode_width, barcode_height, bar_width):

        # 11 bars per character, plus the stop
        num_bars = len(self.bars)

        # Total image width
        image_width = num_bars * bar_width

        image_height = round(image_width/barcode_width*barcode_height)

        img = Image.new('L', (image_width, image_height), 255)

        class BarWriter:
            """Class which moves across the image, writing out bars"""

            def __init__(self, img, bar_height):
                self.img = img
                self.current_x = 0
                self.symbol_top = 0
                self.bar_height = bar_height

            def write_bar(self, value):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                if value == 1:
                    for ypos in range(self.symbol_top, self.bar_height):
                        for xpos in range(self.current_x, self.current_x + bar_width):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar))

        # draw the barcode bars themselves
        writer = BarWriter(img, image_height)
        writer.write_bars(self.bars)

        img = img.resize((round(barcode_width), round(barcode_height)))
        return img


if __name__ == '__main__':
    MULTIPLE = 50
    width = MULTIPLE * 33.8
    height = MULTIPLE * 40.0
    image = Image.new('L', (round(width), round(height)), 255)
    cg = Code128Generate('693417771408', image, {'margin_top': 150, 'margin_bottom': 150})
    cg.write_image()
    draw = ImageDraw.Draw(image)
    image.save('code.jpg', 'jpeg')
