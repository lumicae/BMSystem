# -*- coding:utf-8 -*-
# Python2.7.12
import email
import hashlib
import imaplib
import json
import logging
import poplib
import re
import socket
import sqlite3
import threading
import os
import time
import sys

import binascii

import thread
from pyDes import des, ECB, PAD_PKCS5

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
            protocol = setting['protocol']
            username = setting['username']
            password = setting['password']
            server = setting['server']
            port = setting['port']
            SSL = setting['SSL']
            pwd = DESTool.des_descrpt(str(password), str(username[0:8]))
            return protocol, str(username), pwd, str(server), port, SSL

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
    def do_one_email(cls, emlName, eml_path, parse_file_dir, type="eml", rank=0):
        if rank > 5:
            return
        # 获取邮件信息，把邮件读到内存
        filePointer = FileTool.open_file(eml_path)
        if type == 'attach':
            if "." in emlName:
                md5_value = emlName.split(".")[0]
            else:
                md5_value = emlName
        else:
            md5_value = FileTool.getEmlFileMd5(filePointer)
        filePointer.close()
        filePointer = FileTool.open_file(eml_path)
        mailMsg = cls.getMime(filePointer)
        # 从读到内存的信息中获取邮件头部信息
        #headers = email.parser.Parser().parse(mailMsg)
        mail_attribute = cls.fetchHeader(mailMsg)
        mail_attribute['md5'] = md5_value
        # 从读到内存的信息中获取邮件主体信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        cls.fetchBody(mailMsg, str(emlName), parse_file_dir, rank+1)
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
        mail_attribute['CC'] = cls.parseCC(mailMsg)
        return mail_attribute

    # 获取邮件主体，将正文和附件并保存成文件
    @classmethod
    def fetchBody(cls,mail, emlName, parse_file_dir,rank):
        for part in mail.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = cls.get_charset(part)
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
                        strinfo = re.compile('[:/\*"\<\>：\r\n\?]')
                        b = strinfo.sub('', fname)
                        if rank>1:
                            filepath = parse_file_dir + "\\" + os.path.splitext(emlName)[0] + "_" + b
                        else:
                            filepath = parse_file_dir + "\\" + os.path.splitext(emlName)[0] + "\\" + b
                        FileTool.saveFile(filepath, attachContent)
                        cls.parse_attach_eml(filepath, rank)
                else:
                    if contenttype in ['text/html']:
                        suffix = '.htm'
                        if charset == None:
                            mailContent = part.get_payload(decode=True)
                        else:
                            mailContent = part.get_payload(decode=True).decode(charset)
                        if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                            if rank>1:
                                filepath = parse_file_dir + "\\" + os.path.splitext(emlName)[0] + "_" + u"正文" + suffix
                            else:
                                filepath = parse_file_dir + "\\" + os.path.splitext(emlName)[0]  + "\\" + u"正文" + suffix
                            FileTool.saveFile(filepath, mailContent)
    @classmethod
    def parse_attach_eml(cls, filepath, rank):
        fname = os.path.basename(filepath)
        if fname[-4:] == u'.eml':
            logging.info("if" + fname)
            dir = os.path.dirname(filepath)
            logging.info(dir)
            cls.do_one_email(fname, filepath, dir, "attach", rank)
        else:
            logging.info("else"+fname)
            #logging.info("attach： " + filepath)

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
        strdate = ''
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
            if LOCK.locked():
                LOCK.release()
            logging.error("Date:")
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
            conn = sqlite3.connect(dbpath)
            c = conn.cursor()
            c.execute('DELETE FROM EML_FILE_INFO;')
            logging.info("Table created successfully")
            conn.commit()
            conn.close()
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
                   COL_BOX_TYPE TEXT,\
                   COL_CREATE_TIME INTEGER);')
        logging.info("Table created successfully")
        conn.commit()
        conn.close()
    @classmethod
    def saveToDB(cls, dbpath, mail_attribute):
        create_time = int(time.time())
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        id = mail_attribute['name'].split('.')[0]
        strinfo = re.compile('[\'\"]')
        to = strinfo.sub('', mail_attribute['To'])
        try:
            Cc = strinfo.sub('', mail_attribute['Cc'])
        except Exception,e:
            logging.error(mail_attribute['path'])
            Cc = ""
        subject = strinfo.sub('', mail_attribute['Subject'])
        str_from = strinfo.sub('', mail_attribute['From'])
        name = strinfo.sub('', mail_attribute['name'])
        path = mail_attribute['path'].decode('utf-8', 'ignore')
        owner = mail_attribute['owner'].decode('utf-8', 'ignore')
        date = mail_attribute['Date'].decode('utf-8', 'ignore')
        directory = mail_attribute['directory'].decode('utf-8', 'ignore')
        str_to = to.decode('utf-8', 'ignore')
        try:
            c.execute("INSERT INTO EML_FILE_INFO (id, COL_FILE_NAME, COL_FILE_PATH,\
                                                        COL_TITLE, COL_SENDER,\
                                                        COL_RECIPIENT, COL_CC, COL_OWNER,\
                                                        COL_SEND_DATE, COL_BOX_TYPE, COL_CREATE_TIME) \
                                                        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" \
                      % (id, name, path, \
                         subject, str_from, \
                         str_to, Cc, owner,\
                         date, directory, create_time))
        except Exception,e:
            print e
        conn.commit()
        conn.close()

def saveMailAttribute(dbpath, mail_attribute):
    if os.path.exists(dbpath) is not True:
        fobj = open(dbpath, 'wb')
        fobj.close()
    DBTool.saveToDB(dbpath, mail_attribute)

class DESTool:
    def __init__(self):
        pass
    @classmethod
    def des_encrypt(cls, s, key):
        iv = key
        k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(s, padmode=PAD_PKCS5)
        return binascii.b2a_hex(en)

    @classmethod
    def des_descrpt(cls, s, key):
        iv = key
        k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
        return de


class Parse(threading.Thread):
    def __init__(self, db_path, username, eml_path, eml_count, files_path, box_type="inbox"):
        threading.Thread.__init__(self)
        self.db_path = db_path
        self.eml_path = eml_path
        self.eml_count = eml_count
        self.username = username
        self.files_path = files_path
        self.box_type = box_type
    def run(self):
        parse_file_dir = self.files_path + "\\parsed"
        eml_name = os.path.basename(self.eml_path)
        filePointer = FileTool.open_file(self.eml_path)
        if filePointer != None:
            filePointer.close()
            mail_attribute = EMLTool.do_one_email(eml_name, self.eml_path, parse_file_dir,rank=0)
            mail_attribute['directory'] = self.box_type
            if len(mail_attribute)>0:
                mail_attribute['name'] = eml_name
                mail_attribute['path'] = self.eml_path
                mail_attribute['owner'] = self.username
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
            db_lock.acquire()
            saveMailAttribute(self.db_path, mail_attribute)
            db_lock.release()
            data = {"username": self.username, "status": "parse", "result": str(self.eml_count)}
            info_str = json.dumps(data)
            send_msg(info_str)

class POP3Excutor(threading.Thread):
    def __init__(self, username, password, server, port, useSSL, db_path, files_path):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.useSSL = useSSL
        self.files_path = files_path
        self.db_path = db_path
        self.kill = False
        self.threads = []
    def run(self):
        if self.getConn():
            self.down_parse()
            for thread in self.threads:
                if thread.isAlive():
                    thread.join()
            self.pop_server.quit()
            logging.info("task: %s parse success" % self.username)
            file_num = 0
            file_dir = self.files_path + "\\parsed"
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    ext = file.split(".")[-1]
                    #print file, ext
                    if ext != "eml":
                        file_num = file_num + 1
            #print file_num
            data = {"username":self.username, "status":"parse", "result":"finished", "file_num":str(file_num)}
            info_str = json.dumps(data)
            send_msg(info_str)
        else:
            data = {"username": self.username, "status": "login", "result": "error"}
            info_str = json.dumps(data)
            send_msg(info_str)


    def getConn(self):
        try:
            if self.useSSL == '1':
                self.pop_server = poplib.POP3_SSL(self.server, self.port)
            else:
                self.pop_server = poplib.POP3(self.server, self.port)
            re =  self.pop_server.user(self.username)
            logging.info(re)
            re = self.pop_server.pass_(self.password)
            logging.info(re)
            eml_num, eml_total_size = self.pop_server.stat()
            logging.info('Message: %s, Size: %d' % (eml_num, eml_total_size))
            data = {"username": self.username, "status": "login", "result": str(eml_num)}
            info_str = json.dumps(data)
            send_msg(info_str)
        except Exception, e:
            logging.error(e)
            return False
        else:
            logging.info("task: %s connect success" %self.username)
            return True

    def down_parse(self):
        index_list = self.pop_server.list()[1]
        total = len(index_list)
        step = 10
        rate = total / step
        count = 0
        for tt in range(rate + 1):
            min = tt * step
            if (tt + 1) * step > total:
                max = total
            else:
                max = (tt + 1) * step
            tempList = index_list[min:max]
            for msg_id in tempList:
                count = count + 1
                logging.info(msg_id)
                if self.kill:
                    return
                try:
                    tt = self.pop_server.retr(msg_id)
                    data = "\n".join(tt[1])
                except Exception,e1:
                    logging.info(e1)
                    try:
                        tt = self.pop_server.retr(msg_id.split(" ")[0])
                        data = "\n".join(tt[1])
                    except Exception,e2:
                        logging.info(e2)
                        continue
                hash_name = hashlib.md5(data).hexdigest()
                eml_path = self.files_path + "\\eml\\" + hash_name + ".eml"
                dir = os.path.dirname(eml_path)
                if os.path.exists(dir) is not True:
                    os.makedirs(dir)
                if os.path.exists(eml_path):
                    logging.info("eml repeated %s" % (count))
                else:
                    with open(eml_path, 'wb') as outf:
                        outf.write(data)
                    logging.info("task: %s downlaod %s eml success " % (self.username, count))
                    data = {"username": self.username, "status": "download", "result": str(count)}
                    info_str = json.dumps(data)
                    send_msg(info_str)
                    parser = Parse(self.db_path, self.username, eml_path, count, self.files_path)
                    parser.start()
                    self.threads.append(parser)
            for thread in self.threads:
                if thread.isAlive():
                    thread.join(timeout=10)
        data = {"username": self.username, "status": "download", "result": "finished"}
        info_str = json.dumps(data)
        send_msg(info_str)
        self.kill = True

class IMAPExcutor(threading.Thread):
    def __init__(self, username, password, server, port, useSSL, db_path, files_path):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.useSSL = useSSL
        self.files_path = files_path
        self.db_path = db_path
        self.kill = False
        self.threads = []
    def run(self):
        if self.getConn():
            self.down_parse()
            for thread in self.threads:
                if thread.isAlive():
                    thread.join()
            if self.imap_server.state == 'AUTH':
                self.imap_server.logout()
            else:
                print self.imap_server.state
                self.imap_server.close()
                self.imap_server.logout()
            logging.info("task: %s parse success" % self.username)
            file_num = 0
            file_dir = self.files_path + "\\parsed"
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    ext = file.split(".")[-1]
                    #print file, ext
                    if ext != "eml":
                        file_num = file_num + 1
            #print file_num
            data = {"username": self.username, "status": "parse", "result":"finished", "file_num":str(file_num)}
            info_str = json.dumps(data)
            send_msg(info_str)
        else:
            data = {"username": self.username, "status": "login", "result": "error"}
            info_str = json.dumps(data)
            send_msg(info_str)

    def getConn(self):
        if self.useSSL == "1":
            self.imap_server = imaplib.IMAP4_SSL(self.server, self.port)
        else:
            self.imap_server = imaplib.IMAP4(self.server, self.port)
        try:
            self.imap_server.login(self.username, self.password)
        except Exception, e:
            logging.error(e)
            return False
        else:
            logging.info(str(self.username)+str(self.password))
            logging.info('login success')
            return True

    def down_parse(self):
        obj = self.imap_server.list()
        dir_str = obj[1]
        dir_arr = []
        try:
            count = 0
            for item in dir_str:
                if '"."' in item:
                    separator = "."
                if '"/"' in item:
                    separator = "/"
                dir_arr.append(item.split(separator)[1])
                dir = item.split('"' + separator + '" "')[1]
                # INBOX Drafts Sent Trash Junk
                # 默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
                try:
                    resp, eml_num = self.imap_server.select(dir.strip('"'))
                except Exception,e:
                    continue
                    logging.info("select exception:")
                    logging.error(e)
                    self.imap_server.logout()
                    self.getConn()
                    resp, eml_num = self.imap_server.select(dir.strip('"'))
                if resp != 'OK':
                    logging.info(resp  + "," + eml_num[0])
                    data = {"username": self.username, "status": "login", "result": "error"}
                    info_str = json.dumps(data)
                    send_msg(info_str)
                    return
                else:
                    count = count + int(eml_num[0])
                # 邮件状态设置， 新邮件为Unseen
                # Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
            data = {"username": self.username, "status": "login", "result": str(count)}
            info_str = json.dumps(data)
            send_msg(info_str)
        except Exception,e:
            logging.error(e)
            logging.error(dir_str)
            data = {"username": self.username, "status": "login", "result": "error"}
            info_str = json.dumps(data)
            send_msg(info_str)
            return
        count = 0
        for item in dir_str:
            lower_item = item.lower()
            if "inbox" in lower_item:
                box_type = "inbox"
            elif "drafts" in lower_item:
                box_type = "drafts"
            elif "trash" in lower_item:
                box_type = "trash"
            elif "sent" in lower_item:
                box_type = "outbox"
            elif "junk" in lower_item:
                box_type = "delete"
            else:
                box_type = "others"
            if '"."' in item :
                separator = "."
            if '"/"' in item:
                separator = "/"
            logging.info(item)
            dir_arr.append(item.split(separator)[1])
            dir = item.split('"' + separator + '" "')[1]
            logging.info(dir)
            # INBOX Drafts Sent Trash Junk
            # 默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
            try:
                resp, eml_num = self.imap_server.select(dir.strip('"'))
            except Exception, e:
                continue
                logging.info("select exception:")
                logging.error(e)
                self.imap_server.logout()
                self.getConn()
                resp, eml_num = self.imap_server.select(dir.strip('"'))
            # 邮件状态设置， 新邮件为Unseen
            # Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
            for i in range(int(eml_num[0])):
                count = count + 1
                if self.kill:
                    return
                time.sleep(1)
                try:
                    resp, mailData = self.imap_server.fetch(i+1, "(RFC822)")
                except Exception as e:
                    logging.error(e)
                else:
                    try:
                        mailText = mailData[0][1]
                        hash_name = hashlib.md5(mailText).hexdigest()
                        logging.info(hash_name + " " + str(i))
                        emlpath = self.files_path + "\\eml\\" + hash_name + ".eml"
                        dir = os.path.dirname(emlpath)
                        if os.path.exists(dir) is not True:
                            os.makedirs(dir)
                        if os.path.exists(emlpath):
                            logging.info("eml repeated %s" %(count))
                        else:
                            with open(emlpath, 'wb') as outf:
                                outf.write(mailText)
                        logging.info("the %s task download %s eml" %(self.username, count))
                        data = {"username": self.username, "status": "download", "result": str(count)}
                        info_str = json.dumps(data)
                        send_msg(info_str)
                        parser = Parse(self.db_path, self.username, emlpath, count, self.files_path, box_type)
                        parser.start()
                        self.threads.append(parser)
                    except Exception,e:
                        logging.info(e)
        data = {"username": self.username, "status": "download", "result": "finished"}
        info_str = json.dumps(data)
        send_msg(info_str)
        logging.info("the %s task download success" % (self.username))
        self.kill = True

host = '127.0.0.1'
port = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
flag = s.connect_ex((host, port))

def send_msg(message):
    #print message
    s.sendall(message)
    logging.info(message)


if __name__ == '__main__':
    cur_user_dir = os.path.dirname(sys.path[0])
    root_dir = cur_user_dir + "\\MailDetect"
    log_path = root_dir + "\\log\\" + "test_config.log"
    log_dir = root_dir + "\\log"

    if os.path.exists(log_dir) is False:
        os.makedirs(log_dir)
    file = open(log_path, 'w')
    file.close()
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    json_path = root_dir + "\\config\\" + "email_config.json"
    db_path = root_dir + "\\DB\\" + "emlinfo.db"
    settings = FileTool.read_json_file(json_path)
    DBTool.createDB(db_path)
    logging.info(root_dir)
    files_path = root_dir + "\\mailfile\\" + settings[1]
    set1 = (db_path, files_path)
    set2 = settings[1:] + set1
    logging.info(settings)
    if settings[0] == 'pop3':
        pe = POP3Excutor(*set2)
        pe.start()
        pe.join()
        s.close()
    elif settings[0] == 'imap':
        ie = IMAPExcutor(*set2)
        ie.start()
        ie.join()
        s.close()
