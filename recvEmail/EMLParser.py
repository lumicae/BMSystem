# -*- coding:utf-8 -*-
# Python2.7.12

import os
import hashlib
import email
import threading
import time
import json
import re
import thread
import EMLDB
import Listener

lock = threading.Lock()
LOCK = thread.allocate_lock()
def open_file(filename):
    try:
        f = open(filename, 'rb')
    except:
        print 'can not read file:', filename
    else:
        #print 'success read a file: ', filename
        return f

def getEmlFileMd5(f):
    hash_func = hashlib.md5()
    while True:
        b = f.read(8096)
        if not b:
            break
        hash_func.update(b)
    return hash_func.hexdigest()

#处理邮件
def do_one_email(emlName, eml_path, dir, type="eml", rank=0):
    if rank>5:
        return
    filePointer = open_file(eml_path)
    if type == 'attach':
        if "." in emlName:
            md5_value = emlName.split(".")[0]
        else:
            md5_value = emlName
    else:
        md5_value = getEmlFileMd5(filePointer)
    filePointer.close()
    mail_attribute = {}
    mail_attribute['md5'] = md5_value
    try:
        # 获取邮件信息，把邮件读到内存
        filePointer = open_file(eml_path)
        mailMsg = getMime(filePointer)
        filePointer.close()
        # 从读到内存的信息中获取邮件头部信息
        #headers = email.parser.Parser().parse(mailMsg)
        fetchHeader(mailMsg, mail_attribute)
        # 从读到内存的信息中获取邮件主体信息
        fetchBody(mailMsg, md5_value, dir, rank+1)
    except Exception, e:
        print e
        print eml_path
    return mail_attribute


# 获取邮件内容
def getMime(filepointer):
    try:
        mail = email.message_from_file(filepointer)
    except Exception,e:
        print e
        print filepointer
    return mail

def fetchHeader(mailMsg, mail_attribute):
    mail_attribute['From'] = parseFrom(mailMsg)
    mail_attribute['To'] = parseTo(mailMsg)
    mail_attribute['Subject'] = parseSubject(mailMsg)
    mail_attribute['Date'] = parseDate(mailMsg)
    mail_attribute['Cc'] = parseCC(mailMsg)
    mail_attribute['Bcc'] = parseBcc(mailMsg)

# 获取邮件主体，将正文和附件并保存成文件
def fetchBody(mail, emlName, dir, rank):
    for part in mail.walk():
        if not part.is_multipart():
            contenttype = part.get_content_type()
            filename = part.get_filename()
            charset = get_charset(part)
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
                #print('Attachment:' + fname)
                #保存附件
                if fname != None or fname != '':
                    strinfo = re.compile('[?:/\*"\<\>：\r\n\|\\\]')
                    b = strinfo.sub('', fname)
                    try:
                        lock.acquire()
                        filepath = dir + "\\" + emlName + "\\" + b
                        saveFile(filepath, attachContent)
                        lock.release()
                        parse_attach_eml(filepath, rank)
                    except Exception,e:
                        if lock.locked():
                            lock.release()
                else:
                    print 'fname', fname
            else:
                '''
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                '''
                if contenttype in ['text/html']:
                    suffix = '.htm'
                    if charset == None:
                        mailContent = part.get_payload(decode=True)
                    else:
                        mailContent = part.get_payload(decode=True).decode(charset)
                    if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                        try:
                            lock.acquire()
                            saveFile(dir + "\\" + emlName  + "\\" + u"正文" + suffix, mailContent)
                            lock.release()
                        except Exception,e:
                            if lock.locked():
                                lock.release()
                    else:
                        print 'mailContent', mailContent
                        print '\n'

def parse_attach_eml(filepath, rank):
    fname = os.path.basename(filepath)
    if fname[-4:] == u'.eml':
        dir = os.path.dirname(filepath)
        do_one_email(fname, filepath, dir, "attach", rank)
    else:
        pass

def saveFile(path, data):
    #print path
    dir = os.path.dirname(path)
    if os.path.exists(dir) is not True:
        os.makedirs(dir)
    with open(path, 'wb') as outf:
        outf.write(data)

#字符编码转换方法
def my_unicode(s, encoding):
    if encoding:
        return unicode(s, encoding, 'ignore')
    else:
        ds = s.decode('utf-8', 'ignore')
        return unicode(ds)

def get_charset(message, default='ascii'):
    try:
        return message.get_charset()
    except:
        return default

def parseSubject(data):
    try:
        subject = email.Header.decode_header(data["subject"])
        strsub = my_unicode(subject[0][0], subject[0][1])
    except Exception,e:
        #print e
        strsub = "special subject"
    #if len(strsub) == 0 :
    #    strsub = u"无主题"
    return strsub

def parseFrom(data):
    try:
        if data["From"] != None:
            ls = data["From"].split('<')
            if (len(ls) == 2):
                strinfo = re.compile('["\']')
                b = strinfo.sub('', ls[0])
                fromname = email.Header.decode_header(b)
                strfrom = my_unicode(fromname[0][0], fromname[0][1]) + "<" + ls[1]
            else:
                strfrom = data["From"]
            return strfrom
        else:
            return ""
    except Exception,e:
        #print "From:"
        #print e
        return ""
def parseTo(data):
    try:
        tostr = data['to']
        if ',' in tostr:
            toList = tostr.split(',')
            toArray = []
            for item in toList:
                if '<' in item:
                    itemi = item.split('<')
                    toname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
                    toObj = my_unicode(toname[0][0], toname[0][1]) + "<" + itemi[1]
                    toArray.append(toObj)
                else:
                    toArray.append(item)
            temp = json.dumps(toArray).decode("unicode-escape")
            strTo = temp[1:-1]
        else:
            if '<' in tostr:
                item = tostr.split('<')
                toname = email.Header.decode_header((item[0].strip()).strip('\"'))
                strTo = my_unicode(toname[0][0], toname[0][1]) + "<" + item[1]
            else:
                strTo = tostr
    except Exception,e:
        #print "To: "
        #print tostr
        strTo = ""
    return strTo

def parseCC(data):
    try:
        ccstr = data['Cc']
        if ',' in ccstr:
            ccList = ccstr.split(',')
            ccArray = []
            for item in ccList:
                if '<' in item:
                    itemi = item.split('<')
                    ccname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
                    ccObj = my_unicode(ccname[0][0], ccname[0][1]) + "<" + itemi[1]
                    ccArray.append(ccObj)
                else:
                    ccArray.append(item)
            temp = json.dumps(ccArray).decode("unicode-escape")
            strCc = temp[1:-1]
        else:
            if '<' in ccstr:
                item = ccstr.split('<')
                ccname = email.Header.decode_header((item[0].strip()).strip('\"'))
                strCc = my_unicode(ccname[0][0], ccname[0][1]) + "<" + item[1]
            else:
                strCc = ccstr
    except:
        strCc = ""
        #print ccstr
    return strCc

def parseBcc(data):
    try:
        bccstr = data['Bcc']
        if ',' in bccstr:
            bccList = bccstr.split(',')
            bccArray = []
            for item in bccList:
                if '<' in item:
                    itemi = item.split('<')
                    bccname = email.Header.decode_header((itemi[0].strip()).strip('\"'))
                    bccObj = my_unicode(bccname[0][0], bccname[0][1]) + "<" + itemi[1]
                    bccArray.append(bccObj)
                else:
                    bccArray.append(item)
            temp = json.dumps(bccArray).decode("unicode-escape")
            strBcc = temp[1:-1]
        else:
            if '<' in bccstr:
                item = bccstr.split('<')
                bccname = email.Header.decode_header((item[0].strip()).strip('\"'))
                strBcc = my_unicode(bccname[0][0], bccname[0][1]) + "<" + item[1]
            else:
                strBcc = bccstr
    except:
        strBcc = ""
    return strBcc

def parseDate(data):
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
        #print "Date:"
        #print data["Date"]
        strdate = ''
        if LOCK.locked():
            LOCK.release()
    return strdate

def saveMailAttribute(dbpath, mail_attribute):
    try:
        EMLDB.DBTool.lock.acquire()
        if os.path.exists(dbpath) is not True:
            fobj = open(dbpath, 'wb')
            fobj.close()
        EMLDB.DBTool.saveToDB(dbpath, mail_attribute)
        EMLDB.DBTool.lock.release()
    except Exception,e:
        print e
        if EMLDB.DBTool.lock.locked():
            EMLDB.DBTool.lock.release()

def replyToWeb(taskId, username, emlCount):
    if username == '':
        task_type = 'local'
    else:
        task_type = username
    data = {'taskId':taskId, "from":task_type, "operation": "parse", "result":"success"}
    json_str = json.dumps(data)
    thread.start_new_thread(Listener.sendMsg, (json_str,))

class Parse(threading.Thread):
    def __init__(self, db_path, taskId, emlPath, emlCount, username, rootDir, box_type='inbox'):
        threading.Thread.__init__(self)
        self.db_path = db_path
        self.task_id = taskId
        self.eml_path = emlPath
        self.eml_count = emlCount
        self.username = username
        self.rootDir = rootDir
        self.box_type = box_type
    def run(self):
        dir = self.rootDir + "\\parsed"
        if self.username != '':
            dir = dir + "\\" + self.username
        eml_name = os.path.basename(self.eml_path)
        filePointer = open_file(self.eml_path)
        if filePointer != None:
            filePointer.close()
            mail_attribute = do_one_email(eml_name, self.eml_path, dir, rank=0)
            mail_attribute['box_type'] = self.box_type
            if len(mail_attribute)>0:
                mail_attribute['name'] = eml_name
                mail_attribute['path'] = self.eml_path
                mail_attribute['username'] = self.username
            else:
                mail_attribute['name'] = eml_name
                mail_attribute['path'] = self.eml_path
                mail_attribute['username'] = ""
                mail_attribute['md5'] = ""
                mail_attribute['From'] = ""
                mail_attribute['To'] = ""
                mail_attribute['Subject'] = ""
                mail_attribute['Date'] = ""
                mail_attribute['Cc'] = ""
                mail_attribute['Bcc'] = ""
            saveMailAttribute(self.db_path, mail_attribute)
            replyToWeb(self.task_id, self.username, self.eml_count)
