# -*- coding:utf-8 -*-
# Python2.7.12
import imaplib
import json
import poplib

import threading

import DESTool
import EMLDB
import EMLDownloader
import thread

import FileTest
from Listener import sendMsg

class Controller(threading.Thread):
    threads = {}
    taskIdList = []
    q = threading.Lock()

    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message

    def run(self):
        taskInfo = json.loads(self.message)
        taskId = taskInfo['taskId']
        operation = taskInfo['operation']
        if operation == 'test_account':
            username = taskInfo['username']
            password = taskInfo['password']
            pwd = DESTool.des_descrpt(str(password), str(username[0:8]))
            protocol = taskInfo['protocol']
            server_addr = taskInfo['server']
            port = taskInfo['port']
            useSSL = taskInfo['useSSL']
            if protocol == "imap":
                try:
                    if useSSL == "1":
                        server = imaplib.IMAP4_SSL(str(server_addr), port)
                    else:
                        server = imaplib.IMAP4(str(server_addr), port)
                except Exception, e:
                    result = "server_error"
                else:
                    try:
                        server.login(username, pwd)
                    except:
                        result = "account_error"
                    else:
                        server.logout()
                        result = "connect"
            elif protocol == "pop3":
                try:
                    if useSSL == "1":
                        server = poplib.POP3_SSL(str(server_addr), port)
                    else:
                        server = poplib.POP3(str(server_addr), port)
                except Exception, e:
                    result = "server_error"
                else:
                    try:
                        server.user(username)
                        server.pass_(pwd)
                    except:
                        result = "account_error"
                    else:
                        server.quit()
                        result = "connect"
            else:
                result = "protocol_error"
            data = {'taskId': taskId, "operation": "test_account", "result": result, "username":username}
            json_str = json.dumps(data)
            thread.start_new_thread(sendMsg, (json_str,))
        elif operation == 'test_connection':
            username = taskInfo['username']
            password = taskInfo['password']
            pwd = DESTool.des_descrpt(str(password), str(username[0:8]))
            #1.mail.域名，加密
            #2.mail.域名，不加密
            #3.imap.domain, 加密
            #4.imap.domain,不加密
            #5.pop.domain,加密
            #6.pop.domain,不加密
            #验证用户名，密码
            domain = username.split("@")[1]
            if domain == "163.com" or domain == "126.com" or domain == "yeah.net":
                temp_server_addr = "pop3." + domain
                try:
                    server = poplib.POP3_SSL(str(temp_server_addr), 995)
                except Exception, e:
                    print e
                    try:
                        server = poplib.POP3(str(temp_server_addr), 110)
                    except Exception, e:
                        print e
                        temp_server_addr = "pop." + domain
                        try:
                            server = poplib.POP3_SSL(str(temp_server_addr), 995)
                        except Exception, e:
                            print e
                            try:
                                server = poplib.POP3(str(temp_server_addr), 110)
                            except Exception, e:
                                print e
                                protocol = "none"
                                server_addr = "none"
                                port = 0
                                ssl_flag = 0
                            else:
                                protocol = "pop"
                                port = 110
                                ssl_flag = 0
                                server_addr = temp_server_addr
                        else:
                            protocol = "pop"
                            port = 995
                            ssl_flag = 1
                            server_addr = temp_server_addr
                    else:
                        protocol = "pop3"
                        port = 110
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "pop3"
                    port = 995
                    ssl_flag = 1
                    server_addr = temp_server_addr
            else:
                temp_server_addr = "imap." + domain
                try:
                    server = imaplib.IMAP4_SSL(str(temp_server_addr), 993)
                except Exception, e:
                    print e
                    try:
                        server = imaplib.IMAP4(str(temp_server_addr), 143)
                    except Exception, e:
                        print e
                        temp_server_addr = "mail." + domain
                        try:
                            server = imaplib.IMAP4_SSL(str(temp_server_addr), 993)
                        except Exception, e:
                            print e
                            try:
                                server = imaplib.IMAP4(str(temp_server_addr), 143)
                            except Exception, e:
                                print e
                                temp_server_addr = "pop3." + domain
                                try:
                                    server = poplib.POP3_SSL(str(temp_server_addr), 995)
                                except Exception, e:
                                    print e
                                    try:
                                        server = poplib.POP3(str(temp_server_addr), 110)
                                    except Exception, e:
                                        print e
                                        temp_server_addr = "pop." + domain
                                        try:
                                            server = poplib.POP3_SSL(str(temp_server_addr), 995)
                                        except Exception, e:
                                            print e
                                            try:
                                                server = poplib.POP3(str(temp_server_addr), 110)
                                            except Exception, e:
                                                print e
                                                protocol = "none"
                                                server_addr = "none"
                                                port = 0
                                                ssl_flag = 0
                                            else:
                                                protocol = "pop"
                                                port = 110
                                                ssl_flag = 0
                                                server_addr = temp_server_addr
                                        else:
                                            protocol = "pop"
                                            port = 995
                                            ssl_flag = 1
                                            server_addr = temp_server_addr
                                    else:
                                        protocol = "pop3"
                                        port = 110
                                        ssl_flag = 0
                                        server_addr = temp_server_addr
                                else:
                                    protocol = "pop3"
                                    port = 995
                                    ssl_flag = 1
                                    server_addr = temp_server_addr
                            else:
                                protocol = "imap"
                                port = 143
                                ssl_flag = 0
                                server_addr = temp_server_addr
                        else:
                            protocol = "imap"
                            port = 993
                            ssl_flag = 1
                            server_addr = temp_server_addr
                    else:
                        protocol = "imap"
                        port = 143
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "imap"
                    port = 993
                    ssl_flag = 1
                    server_addr = temp_server_addr
            if protocol == "imap":
                try:
                    server.login(username, pwd)
                    status = "connect"
                except Exception, e:
                    print e
                    status = "account_error"
                server.logout()
            elif protocol == "pop3" or protocol == 'pop':
                try:
                    server.user(username)
                    server.pass_(pwd)
                    status = "connect"
                except Exception, e:
                    print e
                    status = "account_error"
                server.quit()
            elif protocol == "none":
                status = "error"
            if protocol == "imap" and status == "account_error":
                temp_server_addr = "pop3." + domain
                try:
                    server = poplib.POP3_SSL(str(temp_server_addr), 995)
                except Exception, e:
                    print e
                    try:
                        server = poplib.POP3(str(temp_server_addr), 110)
                    except Exception, e:
                        print e
                        temp_server_addr = "pop." + domain
                        try:
                            server = poplib.POP3_SSL(str(temp_server_addr), 995)
                        except Exception, e:
                            print e
                            try:
                                server = poplib.POP3(str(temp_server_addr), 110)
                            except Exception, e:
                                print e
                            else:
                                protocol = "pop"
                                port = 110
                                ssl_flag = 0
                                server_addr = temp_server_addr
                        else:
                            protocol = "pop"
                            port = 995
                            ssl_flag = 1
                            server_addr = temp_server_addr
                    else:
                        protocol = "pop3"
                        port = 110
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "pop3"
                    port = 995
                    ssl_flag = 1
                    server_addr = temp_server_addr
                if protocol == "pop3" or protocol == 'pop':
                    try:
                        server.user(username)
                        server.pass_(pwd)
                        status = "connect"
                    except Exception, e:
                        print e
                        status = "account_error"
                    server.quit()
            if protocol == "pop3" and status == "account_error":
                temp_server_addr = "pop." + domain
                try:
                    server = poplib.POP3_SSL(str(temp_server_addr), 995)
                except Exception, e:
                    print e
                    try:
                        server = poplib.POP3(str(temp_server_addr), 110)
                    except Exception, e:
                        print e
                    else:
                        protocol = "pop"
                        port = 110
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "pop"
                    port = 995
                    ssl_flag = 1
                    server_addr = temp_server_addr
                if protocol == "pop":
                    try:
                        server.user(username)
                        server.pass_(pwd)
                        status = "connect"
                    except Exception, e:
                        print e
                        status = "account_error"
                    server.quit()
            elif protocol == "none":
                status = "error"
            if protocol == "pop3" or protocol == "pop":
                protocol = 'pop3'
            info = {"result":status, "server":server_addr, "port":port, "ssl":ssl_flag, "protocol":protocol}
            info_str = json.dumps(info)
            data = {'taskId': taskId, "operation": "test_connection", "result": info_str, "username":username}
            json_str = json.dumps(data)
            thread.start_new_thread(sendMsg, (json_str,))
        elif operation == 'stop':
            if taskId in Controller.taskIdList:
                try:
                    for ins in Controller.threads[taskId]:
                        if ins.isAlive():
                            ins.kill = True
                    for ins in Controller.threads[taskId]:
                        if ins.isAlive():
                            ins.join()
                    print "terminate|success"
                    data = {'taskId': taskId, "from": "", "operation": "terminate", "result": "success"}
                    json_str = json.dumps(data)
                    thread.start_new_thread(sendMsg, (json_str,))
                except Exception,e:
                    print e
                    data = {'taskId': taskId, "from": "", "operation": "terminate", "result": "fail"}
                    json_str = json.dumps(data)
                    thread.start_new_thread(sendMsg, (json_str,))
            else:
                # 再次开启正在执行的任务
                data = {'taskId': taskId, "from": "", "operation": "terminate", "result": "success"}
                json_str = json.dumps(data)
                thread.start_new_thread(sendMsg, (json_str,))
        else:
            task_from = taskInfo['from']
            filepath = taskInfo['filePath']

            if taskId not in Controller.taskIdList:
                Controller.q.acquire()
                Controller.threads[taskId] = []
                Controller.taskIdList.append(taskId)
                Controller.q.release()
            if task_from  == 'local':
                dbpath = filepath + "\\" + "emlFiles.db"
                EMLDB.DBTool.createDB(dbpath)
                iterator = FileTest.Iterator(dbpath, taskId, filepath)
                Controller.q.acquire()
                Controller.threads[taskId].append(iterator)
                Controller.q.release()
                iterator.start()
            elif task_from == 'directory':
                dbpath = filepath + "\\" + "emlFiles.db"
                EMLDB.DBTool.createDB(dbpath)
                srcPath = taskInfo['sourcePath']
                iterator = FileTest.Iterator(dbpath, taskId, srcPath)
                Controller.q.acquire()
                Controller.threads[taskId].append(iterator)
                Controller.q.release()
                iterator.start()
            elif task_from == 'remote':
                username = taskInfo['username']
                password = taskInfo['password']
                dbpath = filepath + "\\" + username + "\\" + "emlFiles.db"
                EMLDB.DBTool.createDB(dbpath)
                pwd = DESTool.des_descrpt(str(password), str(username[0:8]))
                protocol = taskInfo['protocol']
                server = taskInfo['server']
                port = taskInfo['port']
                useSSL = taskInfo['useSSL']
                if protocol == 'pop3':
                    popTool = EMLDownloader.POP3Tool(username, pwd, server, port, useSSL, filepath, taskId)
                    Controller.q.acquire()
                    Controller.threads[taskId].append(popTool)
                    Controller.q.release()
                    popTool.start()
                elif protocol == 'imap':
                    imapTool = EMLDownloader.IMAPTool(username, pwd, server, port, useSSL, filepath, taskId)
                    Controller.q.acquire()
                    Controller.threads[taskId].append(imapTool)
                    Controller.q.release()
                    imapTool.start()
