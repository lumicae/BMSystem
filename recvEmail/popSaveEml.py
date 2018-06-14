# -*- coding:utf-8 -*-
# Python2.7.12

import poplib
import os
import time
import hashlib
from email.parser import Parser
import email
import json
import re
import base64

def createDir(path):
    if os.path.exists(path) is not True:
        os.makedirs(path)

def saveFile(path, data):
    with open(path, 'wb') as outf:
        outf.write(data)

#字符编码转换方法
def my_unicode(s, encoding):
    if encoding:
        return unicode(s, encoding)
    else:
        ds = s.decode('utf-8', 'ignore')
        return unicode(ds)

def get_charset(message, default='ascii'):
    try:
        return message.get_charset()
    except:
        return default
def parseAddr(item, split):
    s = u''
    pattern = re.compile(r'(\r\n\t)?(\"=\?)(\S+)(\?B\?)(\S+)(\?=")\s(\S+)')
    match = pattern.match(item)
    if match:
        temp = base64.decodestring(match.group(5))
        s += temp.decode(match.group(3), 'ignore')
        s += match.group(7).decode(match.group(3), 'ignore')
        s += split
    return s
def parseFrom(data):
    if data["From"] != None:
        ls = data["From"].split(' <')
        if (len(ls) == 2):
            fromname = email.Header.decode_header((ls[0]).strip('\"'))
            strfrom = 'From:' + my_unicode(fromname[0][0], fromname[0][1]) + "<" + ls[1]
        else:
            strfrom = 'From:' + data["From"]
        return strfrom
    else:
        return ""
def parseTo(data):
    try:
        tostr = data['to']
        if ', ' in tostr:
            toList = tostr.split(', \n\t')
            toArray = []
            for item in toList:
                if ' ' in item:
                    itemi = item.split(' ')
                    toname = email.Header.decode_header((itemi[0]).strip('\"'))
                    toObj = my_unicode(toname[0][0], toname[0][1]) + itemi[1]
                    toArray.append(toObj)
                else:
                    toArray.append(item)
            strTo = "To: " + json.dumps(toArray).decode("unicode-escape")
        else:
            if ' ' in tostr:
                item = tostr.split(' ')
                toname = email.Header.decode_header((item[0]).strip('\"'))
                toObj = my_unicode(toname[0][0], toname[0][1]) + item[1]
                strTo = "To: " + toObj
            else:
                strTo = "To: " + tostr
    except:
        strTo = "To:"
    return strTo
def parseDate(data):
    try:
        dateStr = (data["Date"]).split(" +")[0]
        timeArray = time.strptime(dateStr, "%a, %d %b %Y %H:%M:%S")
        dt_new = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        strdate = 'Date:' + dt_new
    except Exception as e:
        print e
        strdate = 'Date:'
    return strdate
def parseSize(data):
    val = int(data)
    if val>(1024 * 1024):
        t = str(val/(1024*1024)) + "MB"
    elif val>1024:
        t = str(val/1024) + "KB"
    else:
        t = str(val) + "B"
    return "大小：" + t
def parseSubject(data):
    subject = email.Header.decode_header(data["subject"])
    sub = my_unicode(subject[0][0], subject[0][1])
    strsub = 'Subject:' + sub
    return strsub
def parseEml(path, data):
    headers = Parser().parsestr(data)
    print parseSubject(headers)
    print parseFrom(headers)
    print parseTo(headers)
    print parseDate(headers)

    msg = email.message_from_string(data)
    for part in msg.walk():
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
                print 'charset is :', charset
                if charset == None:
                    attachContent = part.get_payload(decode=True)
                else:
                    attachContent = part.get_payload(decode=True).decode(charset)
                print('Attachment:' + fname)
                #保存附件
                if fname != None or fname != '':
                    strinfo = re.compile('[:/\*"\<\>：\r\n]')
                    b = strinfo.sub('', fname)
                    saveFile(path + b, attachContent)
            else:
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                if contenttype in ['text/html']:
                    suffix = '.htm'
                if charset == None:
                    mailContent = part.get_payload(decode=True)
                else:
                    mailContent = part.get_payload(decode=True).decode(charset)
                if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                    saveFile(path + u"正文" + suffix, mailContent)

class saveEmlById():
    def __init__(self, user, pwd, server, rootPath, port):
        self.user = user
        self.pwd = pwd
        self.server = server
        self.rootPath = rootPath
        self.port = port

    def getConn(self):
        self.p = poplib.POP3_SSL(self.server, self.port)
        print self.p.user(self.user)
        print self.p.pass_(self.pwd)
        #print self.p.list()
        eml_num, eml_total_size = self.p.stat()
        print 'Message:%s, Size:%s'%(eml_num, eml_total_size)

    def downloadEml(self):
        for msg_id in self.p.list()[1]:
            print msg_id
            data = "\n".join(self.p.retr(msg_id)[1])
            hash_name = hashlib.md5(data).hexdigest()
            print hash_name
            path = self.rootPath+ "\\" + hash_name + "\\"
            createDir(path)
            parseEml(path, data)
            #saveFile(path, data)
            print parseSize(msg_id.split(' ')[1])

        self.p.quit()


if __name__=="__main__":
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time1 = time.time()
    username = 'lumicae@sina.com'
    passwd = 'liu123456'
    mail_server = 'pop.sina.com'
    #mail_server = "mail.iie.ac.cn"
    #username = "liumingqi@iie.ac.cn"
    #passwd = "liumingqi0709"
    #mail_server = "pop.qq.com"
    #usenrame = "573275629@qq.com"
    #passwd = "wpvvzyuvbkaubege"
    username = "nercis123@163.com"
    passwd = "123qwe"
    mail_server = "pop.163.com"
    rootPath = 'E:\\popEml'
    port = 995
    createDir(rootPath)
    en = saveEmlById(username, passwd, mail_server, rootPath, port)
    en.getConn()
    en.downloadEml()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time2 = time.time()
    contime = str((time2 - time1)/60) + "min"
    print contime



