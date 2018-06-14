# -*- coding:utf-8 -*-
# Python2.7.12
import email
import socket
import sqlite3
import thread

import shutil

import math
import stomp
import os
import sys

#from Listener import Listener
import time

from math import ceil

'''
def sendMsg(message):
    conn = stomp.Connection10([('localhost', 61613)])
    conn.set_listener('', Listener())
    conn.start()
    conn.connect(wait=True)
    conn.send(destination='inspector-reply-queue', body=message, content_type='utf-8')
'''


def getCurrent_Directory():
    dir = os.getcwd()
    diru = os.getcwdu()
    print dir
    print diru
    print sys.path
    t = time.time()
    print int(t)
    import socket
    print socket.gethostname()
    print os.path.dirname(sys.path[0])
if __name__ == "__main__":
    t1 = '111'
    t1 = t1 + '0' * 3
    print t1
    '''
    message = "abc|asddf|erkjk"
    #thread.start_new_thread(sendMsg, (message,))
    #time.sleep(10)
    dir = u"K:\\TestSEt\\eml（源文件）282"
    print os.path.exists(dir)
    dbpath = u"E:\\inspector\\mail\\a3a1baac-4b53-4632-80f7-2c8b37d2e5e1\\emlFiles.db"
    parse_dir = u"E:\\inspector\\mail\\a3a1baac-4b53-4632-80f7-2c8b37d2e5e1\\parsed\\"
    count = 0
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    cursor = c.execute("select COL_FILE_PATH, COL_FILE_NAME ,COL_FILE_HASH from EML_FILE_INFO")
    eml_list = []
    eml_map = {}
    count = 0
    repeat_count = 0
    for row in cursor:
        eml_hash = row[2]
        eml_parse_dir = parse_dir + eml_hash
        if eml_hash in eml_list:
            repeat_count = repeat_count + 1
        else:
            eml_list.append(eml_hash)
        if os.path.exists(eml_parse_dir):
            pass
        else:
            src_path = row[0]
            dis_path = u"K:\\special\\" + row[1]
            shutil.copyfile(src_path, dis_path)
            count = count + 1

    print repeat_count
    
    
    for root, dirs, files in os.walk(dir):
        for emlName in files:
            if emlName not in eml_list:
                print emlName
                count = count +1
                src_path = os.path.join(root, emlName)
                dis_path = u"K:\\special\\" + emlName
                shutil.copyfile(src_path, dis_path)
    
    print count
    conn.close()
    '''
    '''
    str = u'=?gb2312?B?veKVRg==?= <heaven_2004_1986@163.com>'
    itemi = str.split('<')
    toname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
    print toname
    print unicode(toname[0][0], toname[0][1], errors='ignore')
    '''
    '''
    host = '127.0.0.1'
    port = 50007
    s = socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    '''
    '''
    import logging

    logging.basicConfig(filename='myapp.log', level=logging.INFO)

    import subprocess

    ping = subprocess.Popen(["ping", "www.baidu.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = ping.communicate()
    logging.info(out)
    logging.error(error)
    '''
'''
total = 125
    capacity = 10
    step = math.ceil(float(total)/capacity)
    s_step = int(step)
    l = [i+1 for i in range(total)]
    list_list = ([l[i:i+s_step] for i in range(0, len(l), s_step)])
    for list in list_list:
        server.fecth(list)
        server.start()
'''





