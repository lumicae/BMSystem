# -*- coding:utf-8 -*-
# Python2.7.12

import env
from WeixinSpider import *
from spider.Sender.Sender import *
import json
import traceback
from Queue import Queue
import re
import os
import md5
import urlparse
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
		
class WeixinSpiderController():
	def __init__(self):
		print '__init__'
		self.starttime = datetime.datetime.now() #记录启动时间
		self.endtime   = None #记录结束时间

	def clean(self):
		WeixinSpider.Reset()
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
		articleURL = self.localURL + '\\' + self.dirName + '\\' + 'articles'
		imgURL     = self.localURL + '\\' + self.dirName + '\\' + 'images'
 		self.make_dir(articleURL)
		self.make_dir(imgURL)
		WeixinSpider.articleURL = articleURL
		WeixinSpider.imgURL     = imgURL
		Sender.localURL         = self.localURL
		
	def get_task(self, url):
		WeixinSpider.taskQueue.put(url)
		
	def init_spiders(self, ip1, port1, ip2, port2, descriptor):
		#启动WeixinSpider线程
		try:
			print 'start WeixinSpider'
			weixinSpider = WeixinSpider(Sender.queue)
			WeixinSpider.allThread.append(weixinSpider)
			for thread in WeixinSpider.allThread: #启动WeixinSpider线程
				thread.start()
		except:
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
		self.wait_for_children(WeixinSpider.allThread) #等待WeixinSpider线程结束
		self.wait_for_children(Sender.allThread) #等待Sender线程结束
		print 'all thread end'
		self.endtime = datetime.datetime.now()

	#生成报告
	def create_report(self):
		start  = '\n--------date:%s---------' %(self.endtime)
		atc    = 'WeixinSpider download %d articles' %(WeixinSpider.Article_Total)
		img    = 'WeixinSpider download %d images' %(WeixinSpider.Image_Total)
		msg    = 'Sender have sent %d messages' %(Sender.num)
		time   = 'Promgram End, total run:%s seconds' %((self.endtime - self.starttime).seconds)
		end    = '------------------------------------------------'
		return (start, atc, img, msg, time, end)
		
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
	localURL = 'F:\\weixin'
	dirName  = 'shiyan'
	checker_ip   = '127.0.0.1'
	checker_port = 1234
	redis_ip     = '10.10.41.40'
	redis_port   = 6379
	controller = WeixinSpiderController()
	controller.set_localURL(localURL, dirName)
	controller.get_task('并关统计')
	controller.init_dir()
	controller.init_spiders(checker_ip, checker_port, redis_ip, redis_port)
	controller.wait_for_end()
	controller.save_and_exit()
