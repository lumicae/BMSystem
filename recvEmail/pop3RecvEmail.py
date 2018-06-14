# -*- coding:utf-8 -*-
# Python2.7.12

import poplib
import email
from email.parser import Parser

#字符编码转换方法
def my_unicode(s, encoding):
    if encoding:
        return unicode(s, encoding)
    else:
        try:
            return unicode(s)
        except Exception, e:
            print e
            return u'error'
def parseMsg(msg):
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

    print strfrom
    print strdate
    print strsub


class popRecvEmail():
    def __init__(self, host, username, password):
        self.popServer = poplib.POP3(str(host), 110)
        #self.popServer.set_debuglevel(0)
        self.popServer.user(username)
        self.popServer.pass_(password)

    def recvEmail(self):
        emailNum, emailSize = self.popServer.stat()
        print 'email number is %d and size is %d' % (emailNum, emailSize)
        '''
        response, lines, octets = self.popServer.top(1,0)
        print response
        print lines
        print octets
        '''
        number = 1
        for i in range(emailNum):
            number = i
            response, lines, octets = self.popServer.top(i+1, 0)
            print "\n"
            print 'NO:' + str(number)
            number = number + 1
            '''
            for j in range(0, len(lines)):
                import chardet
                encoding = chardet.detect(lines[j])['encoding']
                if encoding:
                    lines[j] = bytes.decode(lines[j], encoding, errors='ignore')
                else:
                    lines[j] = bytes.decode(lines[j])
            '''
            # 利用email库函数转化成Message类型邮件
            msg_content = email.message_from_string('\n'.join(lines))

            # 输出From, To, Subject, Date头部及其信息
            #parseMsg(message[0][1])
            #msg_content = Parser().parsestr(message[0][1])
            content = msg_content.get_payload(decode=True)
            charset = msg_content.get_charset()
            if charset is None:
                content_type = msg_content.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
            filename = msg_content.get_filename()


    def stop(self):
        self.popServer.quit()


if __name__ == '__main__':
    import time
    t1 = time.time()

    host = "mail.nercis.ac.cn"
    username = "liuyi@nercis.ac.cn"
    password = "GTMCmail8800"

    server = popRecvEmail(host, username, password)
    server.recvEmail()
    server.stop()

    t2 = time.time()
    print t2 - t1