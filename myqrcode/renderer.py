"""QR Code renderer"""

from io import BytesIO
try:
    from PIL import Image
except ImportError:
    import Image


class QRCodeRenderer:
    """Rendering class - given a pre-populated QR Code matrix.
    it will add edge handles and render to either to an image
    (including quiet zone) or ascii printout"""

    def __init__(self, matrix):

        self.mtx_size = len(matrix)
        self.matrix = matrix
    # end def __init__

    def add_border(self, colour=1, width=4):
        """Wrap the matrix in a border of given width
            and colour"""

        self.mtx_size += width * 2

        self.matrix = [[colour, ] * self.mtx_size, ] * width + \
                      [[colour, ] * width + self.matrix[i] + [colour, ] * width
                          for i in range(0, self.mtx_size - (width * 2))] + \
                      [[colour, ] * self.mtx_size, ] * width

    def get_pilimage(self, cellsize, colour=0, width=4):
        """Return the matrix as a PIL object"""

        # add the quiet zone (4 x cell width)
        self.add_border(colour=colour, width=width)

        # get the matrix into the right buffer format
        buff = self.get_buffer(cellsize)

        # write the buffer out to an image
        img = Image.frombuffer(
            'L',
            (self.mtx_size * cellsize, self.mtx_size * cellsize),
            buff, 'raw', 'L', 0, -1)
        return img

    def write_file(self, cellsize, filename):
        """Write the matrix out to an image file"""
        img = self.get_pilimage(cellsize)
        img.save(filename)

    def get_imagedata(self, cellsize):
        """Write the matrix out as PNG to an bytestream"""
        imagedata = BytesIO()
        img = self.get_pilimage(cellsize)
        img.save(imagedata, "PNG")
        return imagedata.getvalue()

    def get_buffer(self, cellsize):
        """Convert the matrix into the buffer format used by PIL"""

        def pixel(value):
            """return pixel representation of a matrix value
            0 => white, 1 => black"""
            if value == 0:
                return b"\xff"
            elif value == 1:
                return b"\x00"

        # PIL writes image buffers from the bottom up,
        # so feed in the rows in reverse
        buf = b""
        for row in self.matrix[::-1]:
            bufrow = b''.join([pixel(cell) * cellsize for cell in row])
            for _ in range(0, cellsize):
                buf += bufrow
        return buf

    def get_ascii(self):
        """Write an ascii version of the matrix out to screen"""

        def symbol(value):
            """return ascii representation of matrix value"""
            if value == 0:
                return ' '
            elif value == 1:
                return 'X'
            # end if
        # end def symbol

        return '\n'.join([
            ''.join([symbol(cell) for cell in row])
            for row in self.matrix]) + '\n'
    # end def get_ascii
# end class QRCodeRenderer
