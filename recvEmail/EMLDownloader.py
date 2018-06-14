# -*- coding:utf-8 -*-
# Python2.7.12
import hashlib
import imaplib
import json
import poplib
import os
import thread
import threading

import Controller
import EMLParser
from Listener import sendMsg


def replyToWeb(taskId, emlCount, type, username, file_num):
    data = {'taskId': taskId, "from": username, "operation": type, "result": emlCount, "file_num":file_num}
    json_str = json.dumps(data)
    thread.start_new_thread(sendMsg, (json_str,))

class POP3Tool(threading.Thread):
    def __init__(self, username, password, server, port, useSSL, rootDir, taskId):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.useSSL = useSSL
        self.rootDir = rootDir
        self.taskId = taskId
        self.kill = False
        self.db_path = self.rootDir  + "\\" + username + "\\" + "emlFiles.db"
        self.threads = []

    def run(self):
        if self.getConn():
            self.down_parse()
            self.pop_server.quit()
            for thread in self.threads:
                if thread.isAlive():
                    thread.join()
            file_num = 0
            file_dir = self.rootDir + "\\parsed"
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    ext = file.split(".")[-1]
                    #print file, ext
                    if ext != "eml":
                        file_num = file_num + 1
            print file_num
            replyToWeb(self.taskId, 'finished', 'parse', self.username, str(file_num))
            for ins in Controller.Controller.threads[self.taskId]:
                if ins.kill:
                    Controller.Controller.q.acquire()
                    Controller.Controller.threads[self.taskId].remove(ins)
                    Controller.Controller.q.release()
            if len(Controller.Controller.threads[self.taskId]) == 0:
                Controller.Controller.q.acquire()
                Controller.Controller.taskIdList.remove(self.taskId)
                Controller.Controller.q.release()
        else:
            return False

    def getConn(self):
        try:
            if self.useSSL == '1':
                self.pop_server = poplib.POP3_SSL(str(self.server), self.port)
            else:
                self.pop_server = poplib.POP3(str(self.server), self.port)
            self.pop_server.user(self.username)
            self.pop_server.pass_(self.password)
            eml_num, eml_total_size = self.pop_server.stat()
            print 'Message:%s, Size:%s'%(eml_num, eml_total_size)
        except Exception,e:
            print e
            replyToWeb(self.taskId, "fail", "connect", self.username, '')
            return False
        else:
            replyToWeb(self.taskId, str(eml_num), "connect", self.username, '')
            return True

    def down_parse(self):
        index_list = self.pop_server.list()[1]
        total = len(index_list)
        step = 10
        rate = total / step
        for tt in range(rate + 1):
            min = tt * step
            if (tt + 1) * step > total:
                max = total
            else:
                max = (tt + 1) * step
            tempList = index_list[min:max]
            for msg_id in tempList:
                if self.kill:
                    return
                print msg_id
                try:
                    tt = self.pop_server.retr(msg_id)
                    data = "\n".join(tt[1])
                except Exception,e1:
                    try:
                        tt = self.pop_server.retr(msg_id.split(" ")[0])
                        data = "\n".join(tt[1])
                    except Exception,e2:
                        print e2
                        continue
                hash_name = hashlib.md5(data).hexdigest()
                #print hash_name
                emlpath = self.rootDir + "\\" + self.username + "\\" + hash_name + ".eml"
                dir = os.path.dirname(emlpath)
                if os.path.exists(dir) is not True:
                    os.makedirs(dir)
                if os.path.exists(emlpath) is not True:
                    with open(emlpath, 'wb') as outf:
                        outf.write(data)
                replyToWeb(self.taskId, "success", "download",self.username, '')
                parser = EMLParser.Parse(self.db_path, self.taskId, emlpath, msg_id, self.username, self.rootDir)
                parser.start()
                self.threads.append(parser)
            for thread in self.threads:
                if thread.isAlive():
                    thread.join(timeout=10)
        self.kill = True

class IMAPTool(threading.Thread):
    def __init__(self, username, password, server, port, useSSL, rootDir, taskId):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.useSSL = useSSL
        self.rootDir = rootDir
        self.taskId = taskId
        self.kill = False
        self.db_path = self.rootDir + "\\" + username + "\\" + "emlFiles.db"
        self.threads = []

    '''
    def run(self):
        data = {'taskId': self.taskId, "from": self.username, "operation": "connect", "result": "1000"}
        json_str = json.dumps(data)
        sendMsg(json_str)
        for i in range(1000):
            data = {'taskId': self.taskId, "from": self.username, "operation": "parse", "result": "success"}
            json_str = json.dumps(data)
            sendMsg(json_str)
        replyToWeb(self.taskId, 'finished', 'parse', self.username)
        for ins in Controller.Controller.threads[self.taskId]:
            if ins.kill:
                Controller.Controller.q.acquire()
                Controller.Controller.threads[self.taskId].remove(ins)
                Controller.Controller.q.release()
        if len(Controller.Controller.threads[self.taskId]) == 0:
            Controller.Controller.q.acquire()
            Controller.Controller.taskIdList.remove(self.taskId)
            Controller.Controller.q.release()
    '''
    def run(self):
        if self.getConn():
            self.down_parse()
            self.imap_server.close()
            self.imap_server.logout()
            for thread in self.threads:
                if thread.isAlive():
                    thread.join()
            file_num = 0
            file_dir = self.rootDir + "\\parsed"
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    ext = file.split(".")[-1]
                    #print file, ext
                    if ext != "eml":
                        file_num = file_num + 1
            print file_num
            replyToWeb(self.taskId, 'finished', 'parse', self.username, str(file_num))
            for ins in Controller.Controller.threads[self.taskId]:
                if ins.kill:
                    Controller.Controller.q.acquire()
                    Controller.Controller.threads[self.taskId].remove(ins)
                    Controller.Controller.q.release()
            if len(Controller.Controller.threads[self.taskId]) == 0:
                Controller.Controller.q.acquire()
                Controller.Controller.taskIdList.remove(self.taskId)
                Controller.Controller.q.release()
        else:
            return False

    def getConn(self):
        if self.useSSL == "1":
            self.imap_server = imaplib.IMAP4_SSL(str(self.server), self.port)
        else:
            self.imap_server = imaplib.IMAP4(str(self.server), self.port)
        try:
            self.imap_server.login(self.username, self.password)
        except Exception,e:
            print e
            replyToWeb(self.taskId, "fail", "connect",self.username, '')
            return False
        else:
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
                print dir
                # INBOX Drafts Sent Trash Junk
                # 默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
                resp, eml_num = self.imap_server.select(dir.strip('"'))

                # 邮件状态设置， 新邮件为Unseen
                # Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
                print eml_num[0]
                count = count + int(eml_num[0])
            replyToWeb(self.taskId, count, "connect", self.username, '')
        except Exception,e:
            print e
            replyToWeb(self.taskId, "fail", "connect", self.username, '')
            return
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
            print dir
            # INBOX Drafts Sent Trash Junk
            # 默认为空，"INBOX"表示收件箱，'sent items'表示已发送邮件
            try:
                resp, eml_num = self.imap_server.select(dir.strip('"'))
            except Exception, e:
                continue

            # 邮件状态设置， 新邮件为Unseen
            # Message status = 'All, Unseen, Seen, Recent, Answered, Flagged'
            print eml_num[0]
            total = int(eml_num[0])
            step = 10
            rate = total / step
            for tt in range(rate + 1):
                min = tt * step
                if (tt + 1) * step > total:
                    max = total
                else:
                    max = (tt + 1) * step
                for i in range(min, max):
                    if self.kill:
                        return
                    print i
                    try:
                        resp, mailData = self.imap_server.fetch(i+1, "(RFC822)")
                    except Exception as e:
                        print e
                        continue
                    else:
                        if mailData != None:
                            mailText = mailData[0][1]
                            hash_name = hashlib.md5(mailText).hexdigest()
                            emlpath = self.rootDir + "\\" + self.username + "\\" + hash_name + ".eml"
                            print emlpath
                            dir = os.path.dirname(emlpath)
                            if os.path.exists(dir) is not True:
                                os.makedirs(dir)
                            if os.path.exists(emlpath):
                                pass
                            else:
                                with open(emlpath, 'wb') as outf:
                                    outf.write(mailText)
                                replyToWeb(self.taskId, "success", "download", self.username, '')
                                parser = EMLParser.Parse(self.db_path, self.taskId, emlpath, i, self.username, self.rootDir, box_type)
                                parser.start()
                                self.threads.append(parser)
                        else:
                            print i, 'is null'
        self.kill = True
