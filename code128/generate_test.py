"""Generate test images for code128 barcode encoder"""
from pystrich.code128 import Code128Encoder
from pystrich.code128.test_code128 import Code128Test

for index, string in enumerate(Code128Test.test_strings):
    enc = Code128Encoder(string)
    enc.save("pystrich/code128/test_img/%d.png" % (index + 1))
