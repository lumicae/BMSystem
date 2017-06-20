# -*- coding:utf-8 -*-
# Python2.7.12

import env
from MailSpider import *
from spider.Sender.Sender import *
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
        
class MailSpiderController():
    def __init__(self):
        print '__init__'
        self.starttime = datetime.datetime.now() #记录启动时间
        self.endtime   = None #记录结束时间

    def clean(self):
        MailSpider.Reset()
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
        MailSpider.localURL    = newUrl
        Sender.localURL        = self.localURL
        
    def get_task(self, url):
        MailSpider.taskQueue.put(url)
        
    def init_spiders(self, ip1, port1, ip2, port2, descriptor):
        #启动MailSpider线程
        try:
            print 'start MailSpider'
            weiboSpider = MailSpider(Sender.queue)
            MailSpider.allThread.append(weiboSpider)
            for thread in MailSpider.allThread: #启动MailSpider线程
                thread.start()
        except:
            print 'start MailSpider!'
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
        self.wait_for_children(MailSpider.allThread) #等待MailSpider线程结束
        self.wait_for_children(Sender.allThread) #等待Sender线程结束
        print 'all thread end'
        self.endtime = datetime.datetime.now()

    #生成报告
    def create_report(self):
        start  = '\n--------date:%s--------' %(self.endtime)
        atc    = 'MailSpider had done %d emails' %(MailSpider.Total)
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
    localURL        = ur'D:\Projects\MyWorks\mailspider\code-3'
    dirName         = 'test'
    checker_ip      = '127.0.0.1'
    checker_port    = 1234
    redis_ip        = '10.10.41.45'
    redis_port      = 6379
    task_descriptor = '{"taskid":"id1","dirname":"email_result"}'
    controller = MailSpiderController()
    controller.set_localURL(localURL, dirName)
    controller.get_task(ur'D:\Projects\MyWorks\mailspider\code-3\data\eml')
    controller.init_dir()
    controller.init_spiders(checker_ip, checker_port, redis_ip, redis_port, descriptor = task_descriptor)
    controller.wait_for_end()
    controller.save_and_exit()
