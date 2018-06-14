# -*- coding:utf-8 -*-
# Python2.7.12
import email
import hashlib
import json
import logging
import os
import re
import sqlite3

import thread
import threading

import time

import sys
LOCK = thread.allocate_lock()
db_lock = thread.allocate_lock()
class FileTool():
    def __init__(self):
        pass
    @classmethod
    def read_json_file(cls,path):
        try:
            f = open(path, 'r+')
        except Exception,e :
            logging.error(e)
        else:
            setting = json.loads(f.read())
            f.close()
            db_path = setting["mail_db_path"]
            return db_path

    @classmethod
    def open_file(cls,filename):
        try:
            f = open(filename, 'rb')
        except:
            info = 'can not read file:' + filename
            logging.error(info)
        else:
            info = 'success read a file: ' + filename
            logging.info(info)
            return f
    @classmethod
    def getEmlFileMd5(cls,f):
        hash_func = hashlib.md5()
        while True:
            b = f.read(8096)
            if not b:
                break
            hash_func.update(b)
        return hash_func.hexdigest()
    @classmethod
    def saveFile(cls,path, data):
        dir = os.path.dirname(path)
        if os.path.exists(dir) is not True:
            os.makedirs(dir)
        with open(path, 'wb') as outf:
            outf.write(data)

class EMLTool():
    def __init__(self):
        pass
    #处理邮件
    @classmethod
    def do_one_email(cls,emlName, eml_path, parse_file_dir):
        # 获取邮件信息，把邮件读到内存
        filePointer = FileTool.open_file(eml_path)
        md5_value = FileTool.getEmlFileMd5(filePointer)
        filePointer.close()
        filePointer = FileTool.open_file(eml_path)
        mailMsg = cls.getMime(filePointer)
        # 从读到内存的信息中获取邮件头部信息
        #headers = email.parser.Parser().parse(mailMsg)
        mail_attribute = cls.fetchHeader(mailMsg)
        mail_attribute['md5'] = md5_value
        # 从读到内存的信息中获取邮件主体信息
        cls.fetchBody(mailMsg, str(emlName), parse_file_dir)
        return mail_attribute

    # 获取邮件内容
    @classmethod
    def getMime(cls,filepointer):
        try:
            mail = email.message_from_file(filepointer)
        except Exception,e:
            logging.error(e)
        return mail

    @classmethod
    def fetchHeader(cls, mailMsg):
        mail_attribute = {}
        mail_attribute['From'] = cls.parseFrom(mailMsg)
        mail_attribute['To'] = cls.parseTo(mailMsg)
        mail_attribute['Subject'] = cls.parseSubject(mailMsg)
        mail_attribute['Date'] = cls.parseDate(mailMsg)
        mail_attribute['Cc'] = cls.parseCC(mailMsg)
        return mail_attribute

    # 获取邮件主体，将正文和附件并保存成文件
    @classmethod
    def fetchBody(cls,mail, emlName, parse_file_dir):
        for part in mail.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = cls.get_charset(part)
                #logging.info("filename:"  + filename)
                logging.info("contenttype:" + contenttype)
                if filename:
                    try:
                        import chardet
                        charset1 = chardet.detect(filename)['encoding']
                        h = email.Header.Header(filename, charset=charset1)
                        dh = email.Header.decode_header(h)
                        fname = dh[0][0]
                        encodeStr = dh[0][1]
                        if encodeStr != None:
                            if charset == None:
                                fname = fname.decode(encodeStr, charset1)
                            else:
                                fname = fname.decode(encodeStr, charset)
                    except Exception,e:
                        fname = u'Information Error'
                    if charset == None:
                        attachContent = part.get_payload(decode=True)
                    else:
                        attachContent = part.get_payload(decode=True).decode(charset)
                    logging.info('Attachment:' + fname)
                    #保存附件
                    if fname != None or fname != '':
                        strinfo = re.compile('[:/\*"\<\>：\r\n]')
                        b = strinfo.sub('', fname)
                        FileTool.saveFile(parse_file_dir + "\\" + os.path.splitext(emlName)[0] + "\\" + b, attachContent)
                else:
                    if contenttype in ['text/html']:
                        suffix = '.htm'
                    if contenttype in ['text/plain']:
                        suffix = '.txt'
                    if charset == None:
                        mailContent = part.get_payload(decode=True)
                    else:
                        mailContent = part.get_payload(decode=True).decode(charset)
                    try:
                        if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                            FileTool.saveFile(parse_file_dir + "\\" + os.path.splitext(emlName)[0]  + "\\" + u"正文" + suffix, mailContent)
                    except Exception,e:
                        logging.error(e)
    #字符编码转换方法
    @classmethod
    def my_unicode(cls, s, encoding):
        if encoding:
            return unicode(s, encoding, 'ignore')
        else:
            ds = s.decode('utf-8', 'ignore')
            return unicode(ds)

    @classmethod
    def get_charset(cls, message, default='ascii'):
        try:
            return message.get_charset()
        except:
            return default
    @classmethod
    def parseSubject(cls, data):
        subject = email.Header.decode_header(data["subject"])
        strsub = cls.my_unicode(subject[0][0], subject[0][1])
        return strsub
    @classmethod
    def parseFrom(cls, data):
        try:
            if data["From"] != None:
                ls = data["From"].split('<')
                if (len(ls) == 2):
                    strinfo = re.compile('["\']')
                    b = strinfo.sub('', ls[0])
                    fromname = email.Header.decode_header(b)
                    strfrom = cls.my_unicode(fromname[0][0], fromname[0][1]) + "<" + ls[1]
                else:
                    strfrom = data["From"]
                return strfrom
            else:
                return ""
        except Exception, e:
            logging.info("From:")
            logging.error(e)
            return ""
    @classmethod
    def parseTo(cls, data):
        try:
            tostr = data['to']
            if ',' in tostr:
                toList = tostr.split(',')
                toArray = []
                for item in toList:
                    if '<' in item:
                        itemi = item.split('<')
                        toname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
                        toObj = cls.my_unicode(toname[0][0], toname[0][1]) + "<" + itemi[1]
                        toArray.append(toObj)
                    else:
                        toArray.append(item)
                temp = json.dumps(toArray).decode("unicode-escape")
                strTo = temp[1:-1]
            else:
                if '<' in tostr:
                    item = tostr.split('<')
                    toname = email.Header.decode_header((item[0].strip()).strip('\"'))
                    strTo = cls.my_unicode(toname[0][0], toname[0][1]) + "<" + item[1]
                else:
                    strTo = tostr
        except:
            logging.error("To: ")
            logging.error(tostr)
            strTo = ""
        return strTo
    @classmethod
    def parseDate(cls, data):
        try:
            date_str = data["Date"]
            if len(date_str) > 0:
                if "+" in date_str:
                    dateStr = date_str.split(" +")[0]
                elif "-" in date_str:
                    dateStr = date_str.split(" -")[0]
                else:
                    dateStr = date_str
                if "," in dateStr:
                    temp_str = dateStr.split(",")[1]
                else:
                    temp_str = dateStr
                LOCK.acquire()
                timeArray = time.strptime(temp_str.strip(), "%d %b %Y %H:%M:%S")
                strdate = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                LOCK.release()
        except Exception as e:
            logging.error("Date:")
            logging.error(data["Date"])
            strdate = ''
            if LOCK.locked():
                LOCK.release()
        return strdate
    @classmethod
    def parseCC(cls, data):
        try:
            ccstr = data['Cc']
            if ',' in ccstr:
                ccList = ccstr.split(',')
                ccArray = []
                for item in ccList:
                    if '<' in item:
                        itemi = item.split('<')
                        ccname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
                        ccObj = cls.my_unicode(ccname[0][0], ccname[0][1]) + "<" + itemi[1]
                        ccArray.append(ccObj)
                    else:
                        ccArray.append(item)
                temp = json.dumps(ccArray).decode("unicode-escape")
                strCc = temp[1:-1]
            else:
                if '<' in ccstr:
                    item = ccstr.split('<')
                    ccname = email.Header.decode_header((item[0].strip()).strip('\"'))
                    strCc = cls.my_unicode(ccname[0][0], ccname[0][1]) + "<" + item[1]
                else:
                    strCc = ccstr
        except:
            strCc = ""
        return strCc

class DBTool():
    def __init__(self):
        pass
    @classmethod
    def createDB(cls, dbpath):
        if os.path.exists(dbpath) is True:
            return
        logging.info(os.path.dirname(dbpath))
        if os.path.exists(os.path.dirname(dbpath)) is not True:
            os.makedirs(os.path.dirname(dbpath))
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute('CREATE TABLE EML_FILE_INFO\
                   (id TEXT PRIMARY KEY,\
                   COL_FILE_NAME TEXT,\
                   COL_FILE_PATH TEXT,\
                   COL_TITLE TEXT,\
                   COL_SENDER TEXT,\
                   COL_RECIPIENT TEXT,\
                   COL_CC TEXT,\
                   COL_OWNER TEXT,\
                   COL_SEND_DATE TEXT,\
                   COL_CREATE_TIME INTEGER);')
        logging.info("Table created successfully")
        conn.commit()
        conn.close()
    @classmethod
    def saveToDB(cls, dbpath, mail_attribute):
        db_lock.acquire()

        create_time = int(time.time())
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        id = mail_attribute['md5']
        strinfo = re.compile('[\'\"]')
        to = strinfo.sub('', mail_attribute['To'])
        try:
            Cc = strinfo.sub('', mail_attribute['Cc'])
        except Exception,e:
            logging.error("Cc" + mail_attribute['Cc'])
            Cc = ""
        subject = strinfo.sub('', mail_attribute['Subject'])
        str_from = strinfo.sub('', mail_attribute['From'])
        name = strinfo.sub('', mail_attribute['name'])
        #path = mail_attribute['path'].decode("utf-8", "ignore")
        print id
        try:
            c.execute("INSERT INTO EML_FILE_INFO (id, COL_FILE_NAME, COL_FILE_PATH,\
                                                        COL_TITLE, COL_SENDER,\
                                                        COL_RECIPIENT, COL_CC, COL_OWNER,\
                                                        COL_SEND_DATE, COL_CREATE_TIME) \
                                                        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" \
                      % (id, name, mail_attribute['path'], \
                         subject, str_from, \
                         to, Cc, mail_attribute['owner'],
                         mail_attribute['Date'], create_time))
        except Exception,e:
            logging.error(e)
            logging.error(mail_attribute)
        conn.commit()
        conn.close()
        db_lock.release()

class Parse(threading.Thread):
    def __init__(self, db_path, eml_path, files_path):
        threading.Thread.__init__(self)
        self.db_path = db_path
        self.eml_path = eml_path
        self.files_path = files_path
    def run(self):
        eml_name = os.path.basename(self.eml_path)
        filePointer = FileTool.open_file(self.eml_path)
        if filePointer != None:
            filePointer.close()
            mail_attribute = EMLTool.do_one_email(eml_name, self.eml_path, self.files_path)
            if len(mail_attribute)>0:
                mail_attribute['name'] = eml_name
                mail_attribute['path'] = self.eml_path
                mail_attribute['owner'] = ""
            else:
                mail_attribute['name'] = eml_name
                mail_attribute['path'] = self.eml_path
                mail_attribute['owner'] = ""
                mail_attribute['md5'] = ""
                mail_attribute['From'] = ""
                mail_attribute['To'] = ""
                mail_attribute['Subject'] = ""
                mail_attribute['Date'] = ""
                mail_attribute['Cc'] = ""
            self.saveMailAttribute(mail_attribute)

    def saveMailAttribute(self,mail_attribute):
        if os.path.exists(self.db_path) is not True:
            fobj = open(self.db_path, 'wb')
            fobj.close()
        DBTool.saveToDB(self.db_path, mail_attribute)

if __name__ == '__main__':
    #获取当前执行文件的所在父目录的绝对路径
    root_dir = os.path.dirname(sys.argv[0])
    log_path = root_dir + "\\ParseEml.log"
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    json_path = root_dir + "\\config.json"
    db_path= FileTool.read_json_file(json_path)
    DBTool.createDB(db_path)
    eml_path = sys.argv[1]
    files_path = sys.argv[2]
    threads = []
    DBTool.createDB(db_path)
    logging.info("src_path:" + eml_path)
    logging.info("des_path:" + files_path)
    for root, dirs, files in os.walk(eml_path):
        total = len(files)
        step = 100
        rate = total / step
        count = 0
        logging.info(rate)
        logging.info(files)
        for tt in range(rate + 1):
            min = tt * step
            if (tt + 1) * step > total:
                max = total
            else:
                max = (tt + 1) * step
            tempList = files[min:max]
            for emlName in tempList:
                if emlName[-4:] == u'.eml':
                    emlPath = os.path.join(root, emlName)
                    logging.info(emlPath)
                    parser = Parse(db_path, emlPath, files_path)
                    try:
                        parser.start()
                    except Exception, e:
                        logging.error(e)
                        logging.error(emlPath)
                    threads.append(parser)
            for thread in threads:
                if thread.isAlive():
                    thread.join()
