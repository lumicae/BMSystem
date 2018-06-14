# -*- coding:utf-8 -*-
# Python2.7.12
import json
import threading
import os
import traceback

import thread

import Controller
import EMLParser
import Listener


def replyToWeb(taskId, file_num):
    data = {'taskId': taskId, "from": "local", "operation": "parse", "result": "finished", "file_num": file_num}
    json_str = json.dumps(data)
    thread.start_new_thread(Listener.sendMsg, (json_str,))


class Iterator(threading.Thread):
    def __init__(self, db_path, taskId, srcPath):
        threading.Thread.__init__(self)
        self.kill = False
        self.db_path = db_path
        self.taskId = taskId
        self.srcPath = srcPath
        self.threads = []
    def run(self):
        self.rootDir = os.path.dirname(self.db_path)
        emlCount = 0
        for root, dirs, files in os.walk(self.srcPath):
            total = len(files)
            step = 100
            rate = total/step
            for tt in range(rate+1):
                min = tt * step
                if (tt+1)*step > total:
                    max = total
                else:
                    max = (tt+1)*step
                tempList = files[min:max]
                for emlName in tempList:
                    if self.kill is False:
                        if emlName[-4:] == u'.eml':
                            emlPath = os.path.join(root, emlName)
                            #try:
                            #    print 'eml is', emlPath
                            #except Exception, e:
                            #    traceback.print_exc()
                            parser = EMLParser.Parse(self.db_path, self.taskId, emlPath, emlCount, '', self.rootDir)
                            try:
                                parser.start()
                            except Exception,e:
                                print e
                                print emlPath
                            self.threads.append(parser)
                            print emlCount
                            emlCount += 1
                for thread in self.threads:
                    if thread.isAlive():
                        thread.join()
        print emlCount
        print self.taskId, 'local|parse|finished'
        file_num = 0
        file_dir = self.rootDir + "\\parsed"
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                ext = file.split(".")[-1]
                #print file, ext
                if ext != "eml":
                    file_num = file_num + 1
        print file_num
        replyToWeb(self.taskId, str(file_num))
        Controller.Controller.q.acquire()
        Controller.Controller.threads[self.taskId]=None
        Controller.Controller.taskIdList.remove(self.taskId)
        Controller.Controller.q.release()
        self.kill = True
