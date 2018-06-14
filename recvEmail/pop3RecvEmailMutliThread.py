# -*- coding:utf-8 -*-
# Python2.7.12

import poplib
import email

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

def parseEmail(host, username, password, emlNum, index, step, lock):
    popServer = connServer(host, username, password)
    if index * step > emlNum:
        return
    else:
        min = index * step
        max = (index+1) * step
        for ii in range(min, max):
            number = ii
            response, lines, octets = popServer.top(ii + 1, 0)
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
            message = email.message_from_string('\n'.join(lines))
            # 输出From, To, Subject, Date头部及其信息
            parseMsg(message)

            m = popServer.retr(ii + 1)
            import cStringIO
            buf = cStringIO.StringIO()
            for j in m[1]:
                print >> buf, j
            buf.seek(0)
            #
            msg = email.message_from_file(buf)
            for part in msg.walk():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = get_charset(part)
                fname = parseAttachName(filename, charset)
                if fname:
                    fname = "D:\\" + fname
                    if fname and contenttype == 'application/octet-stream':
                        # save
                        f = open(fname, 'wb')
                        import base64
                        f.write(base64.decodestring(part.get_payload()))
                        f.close()
        lock.release()
        popServer.quit()

def get_charset(message, default='ascii'):
    try:
        return message.get_charset()
    except:
        return default

def parseAttachName(filename, charset):
    if filename:
        try:
            import chardet
            charset1 = chardet.detect(filename)['encoding']
            # s = filename.decode(charset1, 'ignore')
            h = email.Header.Header(filename, charset=charset1)
            dh = email.Header.decode_header(h)
            fname = dh[0][0]
            encodeStr = dh[0][1]
            if encodeStr != None:
                if charset == None:
                    fname = fname.decode(encodeStr, charset1)
                else:
                    fname = fname.decode(encodeStr, charset)
        except Exception, e:
            print e
            # charset = chardet.detect(filename)['encoding']
            # print charset
            # fname = filename.decode(charset)
            fname = u'Information Error'
        return fname

def connServer(host, username, password):
    popServer = poplib.POP3(host)
    popServer.set_debuglevel(0)
    popServer.user(username)
    popServer.pass_(password)
    return popServer

class popRecvEmail():
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def recvEmail(self):
        popServer = connServer(self.host, self.username, self.password)
        emailNum, emailSize = popServer.stat()
        popServer.quit()
        print 'email number is %d and size is %d' % (emailNum, emailSize)
        step = 10
        import thread
        import math
        threadnum = int(math.ceil(emailNum/step))
        locks = [];
        for i in range(threadnum):
            lock = thread.allocate_lock();
            lock.acquire();
            locks.append(lock);
            thread.start_new_thread(parseEmail, (self.host, self.username, self.password, emailNum, i, step, lock))

        for lock in locks:
            while lock.locked():
                pass;


if __name__ == '__main__':
    import time
    t1 = time.time()

    host = "pop.sina.com"
    username = "lumicae@sina.com"
    password = "liumingqi0709"

    server = popRecvEmail(host, username, password)
    server.recvEmail()

    t2 = time.time()
    print t2 - t1