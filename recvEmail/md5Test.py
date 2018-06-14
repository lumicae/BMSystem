# -*- coding:utf-8 -*-
# Python2.7.12

import hashlib
import os

import datetime

def getMaxFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

starttime = datetime.datetime.now()
filename = r'F:\video\Buddies.In.India.2017.WEB-DL.1080p.H264.AAC-MTTV.mp4'
print getMaxFileMd5(filename)
endtime = datetime.datetime.now()
print '运行时间：%ds'%((endtime-starttime).seconds)