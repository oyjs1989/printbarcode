#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#   File Name：     crc_demo
#   Author :        lumi
#   date：          2019/11/5
#   Description :
'''
# - Custom package

# - Third party module of python

# - import odoo package
import binascii

import crc16
# print('0x6EE0') # AD8D69F1163A6ECDD546506D2E1F2F BB  6EE0
# input_data = b'0x83FED3407A939723A5C639B26916D505'# B5C3
input_data = b'0xAD8D69F1163A6ECDD546506D2E1F2FBB' # 6EE0

print(hex(crc16.crc16xmodem(b'AD8D69F1163A6ECDD546506D2E1F2F',int(b'BB',16))))
# import crcmod
# crc16_gen_code = crcmod.Crc(0x13D65, 0xFFFF, True, 0xFFFF)
# print(crc16_gen_code)
# select CRC-16-DNP
# crc16 = crcmod.mkCrcFun(0x8408, 0xFFFF, True, 0xFFFF)

# test
# print(hex(crc16(input_data)))

s = int(input_data, 16)
# a = char2hex(input_data)
# print(a)
# ret = crc16.crc16xmodem(a)
# print(hex(int(ret)))
# crc = crc16.crc16xmodem(b'1234')
# crc = crc16.crc16xmodem(b'56789', crc)
# print(crc)
def checkCRC(message):
    #CRC-16-CITT poly, the CRC sheme used by ymodem protocol
    poly = 0x1021
    #16bit operation register, initialized to zeros
    reg = 0x0000
    #pad the end of the message with the size of the poly
    message += '\x00\x00'
    #for each bit in the message
    for byte in message:
        mask = 0x80
        while(mask > 0):
            #left shift by one
            reg<<=1
            #input the next bit from the message into the right hand side of the op reg
            if ord(byte) & mask:
                reg += 1
            mask>>=1
            #if a one popped out the left of the reg, xor reg w/poly
            if reg > 0xffff:
                #eliminate any one that popped out the left
                reg &= 0xffff
                #xor with the poly, this is the remainder
                reg ^= poly
    return reg

# print(checkCRC(input_data))

def char2hex(data):
#    binascii.b2a_hex(data)
    output = binascii.hexlify(data)
    return output

def crc16(data: bytes, poly=0x1201):
    '''
    CRC-16-CCITT Algorithm
    '''
    data = bytearray(data)
    crc = 0xFFFF
    for b in data:
        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    return crc & 0xFFFF
print(hex(crc16(input_data)))
print(hex(crc16(input_data)))
# def crc16(data: bytearray, offset, length=16):
#     if data is None or offset < 0 or offset > len(data) - 1 and offset + length > len(data):
#         return 0
#     crc = 0xFFFF
#     for i in range(0, length):
#         crc ^= data[offset + i] << 8
#         for j in range(0, 8):
#             if (crc & 0x8000) > 0:
#                 crc = (crc << 1) ^ 0x1021
#             else:
#                 crc = crc << 1
#     return crc & 0xFFFF



# ret = crc16(input_data)
# print(hex(int(ret)))
# print(hex(int('b5c3',16)))


def crc16_ccitt_r(data, crc):
    ccitt16 = 0x8408
    crc = crc ^ int(data)
    for _ in range(8):
        if (crc & 1):
            crc >>= 1
            crc ^= ccitt16
        else:
            crc >>= 1
    return crc
# crc16_ccitt_r(b'a',0xFFFF)
