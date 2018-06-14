# -*- coding:utf-8 -*-
# Python2.7.12
import re
import sqlite3
import threading
import time
import uuid

import os


class DBTool:
    lock = threading.Lock()
    def __init__(self):
        pass

    @classmethod
    def createDB(cls,dbpath):
        try:
            if os.path.exists(dbpath) is True:
                os.remove(dbpath)
        except Exception,e:
            print e
            return
        if os.path.exists(os.path.dirname(dbpath)) is not True:
            os.makedirs(os.path.dirname(dbpath))
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute('CREATE TABLE EML_FILE_INFO\
                   (id TEXT PRIMARY KEY,\
                   COL_ACCOUNT TEXT,\
                   COL_FILE_NAME TEXT,\
                   COL_FILE_PATH TEXT,\
                   COL_FILE_HASH TEXT,\
                   COL_TITLE TEXT,\
                   COL_SENDER TEXT,\
                   COL_RECIPIENT TEXT,\
                   COL_CC TEXT,\
                   COL_BCC TEXT,\
                   COL_SEND_DATE TEXT,\
                   COL_BOX_TYPE TEXT,\
                   COL_CREATE_TIME INTEGER);')
        print "Table created successfully"
        conn.commit()
        conn.close()

    @classmethod
    def saveToDB(cls,dbpath, mail_attribute):
        create_time = int(time.time())
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        strinfo = re.compile('[\'\"]')
        to = strinfo.sub('', mail_attribute['To'])
        try:
            Cc = strinfo.sub('', mail_attribute['Cc'])
        except Exception,e:
            print mail_attribute['Cc']
            Cc = ""
        Bcc = strinfo.sub('', mail_attribute['Bcc'])
        subject = strinfo.sub('', mail_attribute['Subject'])
        str_from = strinfo.sub('', mail_attribute['From'])
        name = strinfo.sub('', mail_attribute['name'])
        print mail_attribute['box_type']
        try:
            c.execute("INSERT INTO EML_FILE_INFO (id, COL_ACCOUNT, COL_FILE_NAME, COL_FILE_PATH,\
                                                        COL_FILE_HASH, COL_TITLE,COL_SENDER,\
                                                        COL_RECIPIENT, COL_CC, COL_BCC, COL_SEND_DATE, COL_BOX_TYPE, COL_CREATE_TIME) \
                                                        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" \
                      % (uuid.uuid1(), mail_attribute['username'], name, mail_attribute['path'], \
                         mail_attribute['md5'], subject, str_from, \
                         to, Cc, Bcc, mail_attribute['Date'], mail_attribute['box_type'], create_time))
        except Exception,e:
            print e
        conn.commit()
        conn.close()