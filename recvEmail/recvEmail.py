# -*- coding:utf-8 -*-
# Python2.7.12
# CreateDate: 2017-12-19

import imaplib
import email
import pprint
import re
import os
import hashlib
import time
import threading
import sys

import thread

import math
from Queue import Queue

reload(sys)
sys.setdefaultencoding('gbk')

#保存文件方法（都是保存在指定的根目录下）
def savefile(filename, data, path):
    strinfo = re.compile('[:/\*"\<\>：\r\n]')
    b = strinfo.sub('', filename)
    try:
        filepath = path + '\\' + b
        #print 'Saved as ' + filepath
        f = open(filepath, 'wb')
    except:
        #print('filename error')
        f.close()
    f.write(data)
    f.close()

#字符编码转换方法
def my_unicode(s, encoding):
    if encoding:
        return unicode(s, encoding, 'ignore')
    else:
        ds = s.decode('utf-8', 'ignore')
        return unicode(ds)

#获得字符编码方法
def get_charset(message, default='ascii'):
    try:
        return message.get_charset()
    except:
        return default
'''
class RecvMail(threading.Thread):
    allThread = []

    def __init__(self, mailhost, account, password, diskroot, port = 993, ssl = 1):
        threading.Thread.__init__(self)
        self.imapServer =
'''
def parseEmail(msg, mypath):

    mailContent = None
    suffix = None
    for part in msg.walk():
        if not part.is_multipart():
            contenttype = part.get_content_type()
            filename = part.get_filename()
            charset = get_charset(part)

            if filename:
                try:
                    import chardet
                    charset1 = chardet.detect(filename)['encoding']
                    #s = filename.decode(charset1, 'ignore')
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
                    print e
                    #charset = chardet.detect(filename)['encoding']
                    #print charset
                    #fname = filename.decode(charset)
                    fname = u'Information Error'
                data = part.get_payload(decode=True)
                #print('Attachment:' + fname)
                #保存附件
                if fname != None or fname != '':
                    savefile(fname, data, mypath)
            else:
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                if contenttype in ['text/html']:
                    suffix = '.htm'
                if charset == None:
                    mailContent = part.get_payload(decode=True)
                else:
                    mailContent = part.get_payload(decode=True).decode(charset)
    return (mailContent, suffix)
#获取邮件方法
def getMail(mailhost, account, password, diskroot, port = 993, ssl = 1):
    mypath = diskroot + "\\" + account
    #是否采用ssl
    if ssl == 1:
        try:
            imapServer = imaplib.IMAP4_SSL(mailhost, port)
        except Exception,e:
            print e
            return
    else:
        imapServer = imaplib.IMAP4(mailhost, port)
    imapServer.login(account, password)
    obj = imapServer.list()
    eml_index_queue = Queue()
    dir_str = obj[1]
    dir_arr = []
    dir_count_arr = {}
    for item in dir_str:
        dir_arr.append(item.split("/")[1])
        dir = item.split('"/" "')[1]
        print dir
        # INBOX Drafts Sent Trash Junk
        #默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
        select_dir = dir.strip('"')
        resp, eml_num =  imapServer.select(select_dir)

        print resp
        print int(eml_num[0])
        total = int(eml_num[0])
        dir_count_arr[select_dir] = total
        for i in range(total):
            obj = {}
            obj["dir_name"] = select_dir
            obj["index"] = i + 1
            eml_index_queue.put(obj)
        #邮件状态设置， 新邮件为Unseen
        #Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
    imapServer.close()
    imapServer.logout()
    fecth_threads = []
    '''
    for item in dir_count_arr.items():
        
        total = item[1]
        if total == 0:
            continue
        select_dir = item[0]
        #step = int(math.ceil(float(total)/thread_num))
        #temp_list = [i + 1 for i in range(total)]
        #list_list = ([temp_list[i:i + step] for i in range(0, len(temp_list), step)])
    '''
    thread_num = 4
    for i in range(thread_num):
        thread_name = "thread_" + str(i)
        fetch = FetchMailData(thread_name, eml_index_queue, account, password, ssl, mailhost, port)
        fetch.start()
        fecth_threads.append(fetch)
    for fetch_thread in fecth_threads:
        if fetch_thread.isAlive():
            fetch_thread.join()





class FetchMailData(threading.Thread):
    def __init__(self, thread_name, eml_index_queue, account, password, ssl, host, port):
        threading.Thread.__init__(self)
        self.eml_index_queue = eml_index_queue;
        self.account = account
        self.password = password
        self.ssl = ssl
        self.host = host
        self.port = port
        self.thread_name = thread_name
    def run(self):
        if self.ssl == 1:
            try:
                imapServer = imaplib.IMAP4_SSL(self.host, self.port)
            except Exception, e:
                print e
                return
        else:
            imapServer = imaplib.IMAP4(self.host, self.port)
        imapServer.login(self.account, self.password)
        while True:
            obj = self.eml_index_queue.get(True)
            if obj == None:
                break
            imapServer.select(obj["dir_name"])
            try:
                print self.thread_name + ":fetch" + str(obj["index"])
                resp, mailData = imapServer.fetch(obj["index"], "(RFC822)")
            except Exception as e:
                print e
                return
            else:
                mailText = mailData[0][1]
                hash_val = hashlib.md5(mailText).hexdigest()
                emlpath = mypath + "\\" + hash_val
                if os.path.exists(emlpath) is not True:
                    os.makedirs(emlpath)
                else:
                    pass
                    #print emlpath
                msg = email.message_from_string(mailText)
                ls = msg["From"].split(' ')
                if (len(ls) == 2):
                    fromname = email.Header.decode_header((ls[0]).strip('\"'))
                    strfrom = 'From:' + my_unicode(fromname[0][0], fromname[0][1]) + ls[1]
                else:
                    strfrom = 'From:' + msg["From"]
                try:
                    strdate = 'Date:' + msg["Date"]
                except:
                    strdate = 'Date:'
                try:
                    strCc = 'Cc:' + msg["Cc"]
                except:
                    strCc = 'Cc:'
                try:
                    strBcc = 'Bcc:' + msg["Bcc"]
                except:
                    strBcc = "Bcc:"
                try:
                    tostr = msg['To']
                    if ', ' in tostr:
                        toList = tostr.split(', ')
                        toArray = []
                        for item in toList:
                            toname = email.Header.decode_header((item[0]).strip('\"'))
                            toObj = my_unicode(toname[0][0], toname[0][1]) + item[1]
                            toArray.append(toObj)
                        strTo = "To: " + str(toArray)
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
                subject = email.Header.decode_header(msg["Subject"])
                sub = my_unicode(subject[0][0], subject[0][1])
                strsub = 'Subject:' + sub

                mailContent, suffix = parseEmail(msg, emlpath)
                '''
                print '\n'
                print 'No:' + str(obj["index"])
                print strfrom
                print strdate
                print strsub
                print strTo
                print strCc
                print strBcc
                '''
                if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                    strinfo = re.compile('[:/\*"\<\>：]')
                    savefile(u"正文" + suffix, mailContent, emlpath)
        imapServer.close()
        imapServer.logout()

if __name__ == '__main__':
    mypath = 'e:\\testRecvMail\\liumingqi@iie.ac.cn'
    print 'begin to get email...'
    user = 'liumingqi@iie.ac.cn'
    server = "mail.iie.ac.cn"
    pwd = "liumingqi0709"
    #user = 'lumicae@bupt.edu.cn'
    #user = 'lumicae@sina.com'
    #pwd = 'liumingqi0709'
    #user = 'liuyi@nercis.ac.cn'
    #pwd = 'GTMCmail8800'
    #server = 'mail.nercis.ac.cn'
    #user = "nercis8@hysml.xyz"
    #pwd = "123qwe"
    #server = "mail.hysml.xyz"
    getMail(server, user, pwd, mypath, 993, 1)
    print 'the end of get email'
