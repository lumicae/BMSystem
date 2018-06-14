# -*- coding:utf-8 -*-
# Python2.7.12
import sqlite3
import threading
import os
import traceback

import thread

import time

import Controller
import EMLParser
import Listener


def replyToWeb(taskId):
    message = taskId + '|parse|finished'
    thread.start_new_thread(Listener.sendMsg, (message,))
    time.sleep(10)

class Iterator(threading.Thread):
    def __init__(self, db_path, taskId, srcPath):
        threading.Thread.__init__(self)
        self.kill = False
        self.db_path = db_path
        self.taskId = taskId
        self.srcPath = srcPath
        self.threads = []
    def run(self):
        emlCount = 0
        for root, dirs, files in os.walk(self.srcPath):
            for emlName in files:
                if self.kill is False:
                    if emlName[-4:] == u'.eml':
                        emlPath = os.path.join(root, emlName)
                        try:
                            print 'eml is', emlPath
                        except Exception, e:
                            traceback.print_exc()
                        emlCount += 1
                        parser = EMLParser.Parse(self.db_path, self.taskId, emlPath, emlCount, '')
                        parser.start()
                        self.threads.append(parser)
                        parser.join()

        for thread in self.threads:
            if thread.isAlive():
                thread.join()
        replyToWeb(self.taskId)
        Controller.Controller.q.acquire()
        Controller.Controller.threads[self.taskId]=None
        Controller.Controller.taskIdList.remove(self.taskId)
        Controller.Controller.q.release()
        self.kill = True
