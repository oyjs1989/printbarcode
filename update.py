# -*- coding: utf-8 -*-

import datetime
import os

new_verison_context = ''
for line in open('file_version_info.txt', 'r'):
    new_line = line.encode('gbk').decode('utf-8')[:-1]
    if 'VersionCode' in new_line:
        versioncode = new_line.strip(':')[-1]
        new_verison_context += "# VersionCode:%s\n" % versioncode
        continue

    if 'ReleaseCode' in new_line:
        releasecode = '%s' % (int(new_line.strip(':')[-1]) + 1)
        new_verison_context += "# ReleaseCode:%s\n" % releasecode
        continue

    if 'filevers=' in new_line:
        new_verison_context += '    filevers=(%s, %s, %s, 0),\n' % (
            datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day)
        continue

    if 'prodvers=' in new_line:
        new_verison_context += '    prodvers = (%s, %s, %s, 0),\n' % (
            datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day)
        continue

    if 'FileVersion' in new_line:
        new_verison_context += "        StringStruct(u'FileVersion', u'2019.10.30.v%s.%s'),\n" % (
            versioncode, releasecode)
        continue

    if 'ProductVersion' in new_line:
        new_verison_context += "        StringStruct(u'ProductVersion', u'2019.10.30.v%s.%s')])\n" % (
            versioncode, releasecode)
        continue

    new_verison_context += '%s\n' % new_line

with open('tmp.txt', 'w') as f:
    f.write(new_verison_context.encode('utf-8').decode('gbk'))
os.remove('file_version_info.txt')
os.rename('tmp.txt', 'file_version_info.txt')
