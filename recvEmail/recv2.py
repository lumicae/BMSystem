# -*- coding:utf-8 -*-
# Python2.7.12
# CreateDate: 2017-12-19

import imaplib
import email
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('gbk')

#保存文件方法（都是保存在指定的根目录下）
def savefile(filename, data, path):
    strinfo = re.compile('[:/\*"\<\>：\r\n|?]')
    b = strinfo.sub('', filename)

    try:
        filepath = path + '\\' + b
        print 'Saved as ' + filepath
        f = open(filepath, 'wb')
    except:
        print('filename error')
        f.close()
    f.write(data)
    f.close()

#字符编码转换方法
def my_unicode(s, encoding):
    try:
        if encoding:
            return unicode(s, encoding)
        else:
            try:
                return unicode(s)
            except Exception, e:
                print e
                return u'error'
    except Exception,e :
        print e
        return u'error'

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
def parseEmail(msg, mypath, subject):

    mailContent = None
    contenttype = None
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
                print('Attachment:' + fname)
                #保存附件
                if fname != None or fname != '':
                    savefile(subject + "_" + fname, data, mypath)
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

def connEmailServer(mailhost, account, password, diskroot, port = 993, ssl = 1):
    # 是否采用ssl
    if ssl == 1:
        imapServer = imaplib.IMAP4_SSL(mailhost, port)
    else:
        imapServer = imaplib.IMAP4(mailhost, port)
    imapServer.login(account, password)
    imapServer.select()
    # 邮件状态设置， 新邮件为Unseen
    # Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
    resp, items = imapServer.search(None, 'All')
    return imapServer, items

def createDir(diskroot, account):
    mypath = diskroot + "\\" + account
    if os.path.exists(mypath) is not True:
        os.makedirs(mypath)

#获取邮件方法
def getMail(mailhost, account, password, diskroot, port = 993, ssl = 1):
    mypath = diskroot + "\\" + account
    if os.path.exists(mypath) is not True:
        os.makedirs(mypath)
    #是否采用ssl
    if ssl == 1:
        imapServer = imaplib.IMAP4_SSL(mailhost, port)
    else:
        imapServer = imaplib.IMAP4(mailhost, port)
    imapServer.login(account, password)
    obj = imapServer.list()
    dir_str = obj[1]
    dir_arr = []
    print dir_str
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
        if '"."' in item:
            separator = "."
        if '"/"' in item:
            separator = "/"
        dir_arr.append(item.split(separator)[1])
        dir = item.split('"' + separator + '" "')[1]

        try:
            resp, eml_num = imapServer.select(dir.strip('"'))
        except Exception,e:
            print e

        # INBOX Drafts Sent Trash Junk
        # 默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
        #草稿箱：Drafts,垃圾箱：Trash
        '''
        ['() "/" "INBOX"', '(\\Drafts) "/" "Drafts"', '(\\Sent) "/" "Sent Items"', '(\\Trash) "/" "Trash"', '(\\Junk) "/" "Junk E-mail"', '() "/" "Virus Items"']

['() "." "Inbox"', '(\\Drafts) "." "&g0l6Pw-"', '(\\Trash) "." "&XfJSIJZkkK5O9g-"', '(\\Sent) "." "&XfJT0ZABkK5O9g-"', '(\\Junk) "." "&V4NXPpCuTvY-"', '() "." "Notice"']
        '''
        #print imapServer.select("INBOX")
        #邮件状态设置， 新邮件为Unseen
        #Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
        #resp, items = imapServer.search(None, 'All')
        number = 1
        print eml_num[0]
        for i in range(int(eml_num[0])):
            try:
                resp, mailData = imapServer.fetch(i+1, "(RFC822)")
            except Exception, e:
                print i
                print e
                #print imapServer.status()
                #imapServer.close()
                try:
                    imapServer.logout()
                    if ssl == 1:
                        imapServer = imaplib.IMAP4_SSL(mailhost, port)
                    else:
                        imapServer = imaplib.IMAP4(mailhost, port)
                    imapServer.login(account, password)
                    resp, eml_num = imapServer.select(dir.strip('"'))
                    resp, mailData = imapServer.fetch(i + 1, "(RFC822)")
                except Exception,e:
                    print e
            else:
                mailText = mailData[0][1]
                msg = email.message_from_string(mailText)
                ls = msg["From"].split(' ')
                strfrom = ''
                if (len(ls) == 2):
                    fromname = email.Header.decode_header((ls[0]).strip('\"'))
                    strfrom = 'From:' + my_unicode(fromname[0][0], fromname[0][1]) + ls[1]
                else:
                    strfrom = 'From:' + msg["From"]
                try:
                    strdate = 'Date:' + msg["Date"]
                except:
                    strdate = 'Date:'
                subject = email.Header.decode_header(msg["Subject"])
                sub = my_unicode(subject[0][0], subject[0][1])
                strsub = 'Subject:' + sub

                mailContent, suffix = parseEmail(msg, mypath, sub)
                print '\n'
                print 'No:' + str(number)
                print strfrom
                print strdate
                print strsub

                if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
                    strinfo = re.compile('[:/\*"\<\>：]')
                    b = strinfo.sub('', sub)
                    savefile(b + suffix, mailContent, mypath)
                    number = number + 1


    imapServer.close()
    imapServer.logout()

if __name__ == '__main__':
    mypath = 'e:\\testRecvMail'
    print 'begin to get email...'
    user = 'lumicae@bupt.edu.cn'
    pwd = 'liumingqi0709'
    server = 'mail.bupt.edu.cn'
    #user = 'liumingqi@iie.ac.cn'
    #pwd = 'liumingqi0709'
    #server = 'mail.iie.ac.cn'
    port = 993
    ssl = 1
    user = "liuyi@nercis.ac.cn"
    pwd = "GTMCmail8800"
    server = "mail.nercis.ac.cn"
    user = 'hrbmj@bjhr.gov.cn'
    pwd = 'bm69696735'
    server = 'mail.bjhr.gov.cn'
    port = 110
    ssl = 0
    user = "nercis123@126.com"
    pwd = "123qwe"
    server = "imap.126.com"
    port = 993
    ssl = 1
    getMail(server, user, pwd, mypath, port, ssl)
    print 'the end of get email'
