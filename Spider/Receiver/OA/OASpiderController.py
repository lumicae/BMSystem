# -*- coding:utf-8 -*-
# Python2.7.12

from OASpider import *
from Spider.Sender.Sender import *
import json
import traceback
from Queue import Queue
import os
import time
import datetime
    
def save_file(dir, content):
    try:
        f = open(dir, 'a+')
        f.write(content)
        f.close() 
    except:
        print 'can not create file:', dir
        return False
    else:
        print 'success create a file: ', dir
        return True
    
def make_dir(url):
    try:
        os.makedirs(url)
    except:
        print '\n%s this dir may be already exist!' %(url)
        return False
    else:
        print 'create a dir:', url
        return True
        
class OASpiderController():
    def __init__(self):
        print '__init__'
        self.starttime = datetime.datetime.now() #记录启动时间
        self.endtime   = None #记录结束时间

    def clean(self):
        OASpider.Reset()
        Sender.Reset()
        
    #设置本地保存数据的路径
    def set_localURL(self, localURL, dirName):
        self.localURL = localURL
        self.dirName  = dirName
        
    #创建目录
    def make_dir(self, url):
        try:
            os.makedirs(url)
        except:
            print '\n%s this dir may be already exist!' %(url)
        
    def init_dir(self):
        newUrl = self.localURL + '\\' + self.dirName
        self.make_dir(newUrl)
        OASpider.localURL    = newUrl
        Sender.localURL        = self.localURL
        
    def init_spiders(self, ip1, port1, ip2, port2, descriptor):
        #启动MailSpider线程
        try:
            print 'start OASpider'
            oaSpider = OASpider(Sender.queue)
            OASpider.allThread.append(oaSpider)
            for thread in OASpider.allThread: #启动MailSpider线程
                thread.start()
        except:
            print 'start OASpider!'
            traceback.print_exc()
        #'''
        #启动Sender线程
        try:
            print 'start Sender'
            sender = Sender(ip1, port1, ip2, port2, descriptor)
            Sender.allThread.append(sender)
            sender.start()
        except:
            print 'start Sender error!'
            traceback.print_exc()
    
    
    #等待所有子线程结束
    def wait_for_children(self, threadList):
        for thread in threadList:
            if thread.isAlive():
                thread.join()
    
    #等待全部线程结束
    def wait_for_end(self):
        print 'wait_for_end'
        self.wait_for_children(OASpider.allThread) #等待MailSpider线程结束
        print 'oaspider thread end'
        self.wait_for_children(Sender.allThread) #等待Sender线程结束
        print 'sender thread end'
        self.endtime = datetime.datetime.now()

    #生成报告
    def create_report(self):
        start  = '\n--------date:%s--------' %(self.endtime)
        atc    = 'OASpider had done %d files' %(OASpider.Total)
        msg    = 'Sender have sent %d messages' %(Sender.num)
        time   = 'Promgram End, total run:%s seconds' %((self.endtime - self.starttime).seconds)
        end    = '------------------------------------------------'
        return (start, atc, msg, time, end)
        
    #结束时显示报告
    def show_end(self, report):    
        for str in report:
            print str
            
    #退出并保存结果
    def save_and_exit(self):
        print 'save_and_exit'
        report = self.create_report()
        result = ''
        for str in report:
            result += str + '\n'
        fileName = self.localURL + '\\' + self.dirName + '\\result.txt'
        save_file(fileName, result)
        self.show_end(report)
        self.clean()

    
if __name__ == '__main__':
    #测试数据
    localURL        = ur'f:\oatest'
    dirName         = 'testoa'
    checker_ip      = '127.0.0.1'
    checker_port    = 1234
    redis_ip        = '127.0.0.1'
    redis_port      = 6379
    task_descriptor = '{"taskid":"oa1","dirname":"oa1dir"}'
    controller = OASpiderController()
    controller.set_localURL(localURL, dirName)
    controller.init_dir()
    controller.init_spiders(checker_ip, checker_port, redis_ip, redis_port, descriptor = task_descriptor)
    controller.wait_for_end()
    controller.save_and_exit()