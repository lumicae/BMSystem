# -*- coding:utf-8 -*-
#!/usr/bin/env python2.7
from WebSpider import *
from spider.Sender.Sender import *
import urlparse
import sys
import os
import datetime
import traceback
import re
import shutil

def delete_dir(dir_path):
	try:
		shutil.rmtree(dir_path)
	except:
		print 'Can not delete %s Maybe not exist.' %(dir_path)
	else:
		print 'Delete %s success.' %(dir_path)
	
class SpiderController():
	def __init__(self):
		print '__init__'
		self.starttime = datetime.datetime.now() #记录启动时间
		self.endtime = None #记录结束时间
		self.kill = False
		self.myChildrenList = []
		
	def clean(self):
		self.kill = False
		self.myChildrenList  = []
		URLSpider.Reset()
		DownloadSpider.Reset()
		Sender.Reset()
		
	#获取任务，首先添加新的域，然后添加到任务队列中
	def get_task(self, url):
	    # if url is xx.xx.xx.xx:yy
		regex_ip = re.compile('.+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*')
		find_ip = re.findall(regex_ip, url)
		if (len(find_ip) != 0):
			domain = find_ip[0]
		else:
			tumple = urlparse.urlparse(url) #解析url成分
			root_domain = tumple.netloc #根域
			current_domain = tumple.netloc + tumple.path #严格的限定域
			domain = root_domain #选用根域
		print 'root_domain: ', domain
		if domain[:4] == 'www.':
			domain = domain[4:]
		if domain not in URLSpider.domainList:
			URLSpider.domainList.append(domain)
		URLSpider.queue.put((None, url, 0))
	
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
	
	#创建保存数据的文件夹
	def init_dir(self):
		print 'init_dir' 
		htmlURL = self.localURL + '\\' + self.dirName + '\\' + 'HTML'
		fileURL = self.localURL + '\\' + self.dirName + '\\' + 'FILE'
		imgURL  = self.localURL + '\\' + self.dirName + '\\' + 'IMG'
		self.make_dir(self.localURL)
		self.make_dir(htmlURL)
		self.make_dir(fileURL)
		self.make_dir(imgURL)
		URLSpider.localURL = htmlURL #设置URLSpider的文件夹路径
		DownloadSpider.fileLocalURL = fileURL #设置DownloadSpider的文件保存路径
		DownloadSpider.imgLocalURL  = imgURL #设置DownloadSpider的图片保存路径
		Sender.localURL = self.localURL
		
		
	#启动爬虫线程
	def init_spiders(self, Num_Of_URLSpider, timeout1, Num_Of_DownloadSpider, timeout2,
						ip1, port1, ip2, port2, descriptor, rank = 0x7fffffff):
		print 'init_spiders'
		#启动URLSpider线程
		try:
			print 'start URLSpider'
			for num in range(Num_Of_URLSpider): #创建URLSpider线程
				urlSpider = URLSpider('URLSpider' + str(num), Sender.queue, timeout1, rank)
				URLSpider.allThread.append(urlSpider)
				self.myChildrenList.append(urlSpider)
				
			for thread in URLSpider.allThread: #启动URLSpider线程
				thread.start()
		except:
			print 'start URLSpider error!'
			traceback.print_exc()
			
		#启动DownloadSpider线程
		try:
			print 'start DownloadSpider'
			for num in range(Num_Of_DownloadSpider): #创建DownloadSpider线程
				downloadSpider = DownloadSpider('DownloadSpider' + str(num), Sender.queue, timeout2)
				DownloadSpider.allThread.append(downloadSpider)
				self.myChildrenList.append(downloadSpider)
				
			for thread in DownloadSpider.allThread: #启动DownloadSpider线程
				thread.start()
		except:
			print 'start DownloadSpider!'
			traceback.print_exc()
		#'''
		#启动Sender线程
		try:
			print 'start Sender'
			sender = Sender(ip1, port1, ip2, port2, descriptor)
			Sender.allThread.append(sender)
			self.myChildrenList.append(sender)
			
			sender.start()
		except:
			print 'start Sender error!'
			traceback.print_exc()
		#'''
	
	def kill_children(self):
		self.kill = True
		for thread in self.myChildrenList:
			thread.kill = True
	
	#等待所有子线程结束
	def wait_for_children(self, threadList):
		for thread in threadList:
			if thread.isAlive():
				thread.join()
	
	#等待全部线程结束
	def wait_for_end(self):
		print 'wait_for_end'
		
		self.wait_for_children(URLSpider.allThread) #等待URLSpider线程结束
		print 'URLSpider end at wait for end.'
		
		self.wait_for_children(DownloadSpider.allThread) #等待DownloadSpider线程结束
		print 'DownloadSpider end at wait for end.'
		
		self.wait_for_children(Sender.allThread) #等待Sender线程结束
		print 'Sender end at wait for end'
		
		print 'all thread end'
		self.endtime = datetime.datetime.now()

	#生成报告
	def create_report(self):
		start  = '\n--------date:%s---------' %(self.endtime)
		web    = 'URLSpider download %d websites' %(URLSpider.Total)
		file   = 'DownloadSpider download %d files' %(DownloadSpider.fileNum)
		img    = 'DownloadSpider download %d imgs' %(DownloadSpider.imgNum)
		msg    = 'Sender have sent %d messages' %(Sender.num)
		time   = 'Promgram End, total run:%s seconds' %((self.endtime - self.starttime).seconds)
		end    = '------------------------------------------------'
		return (start, web, file, img, msg, time, end)
		
	#结束时显示报告
	def show_end(self, report):	
		for str in report:
			print str
			
	#退出并保存结果
	def save_and_exit(self):
		print 'save_and_exit'
		report = self.create_report()
		report_path = self.localURL + '\\' + self.dirName + '\\result.txt'
		try:
			file = open(report_path, 'a+')
			for str in report:
				file.write(str + '\n')
			file.close()
		except:
			print 'Can not write report: ', report_path
		self.show_end(report)
		#if self.kill:      kill附带的删除功能，最后决定不附带该功能
		#	dir_path = self.localURL + '\\' + self.dirName
		#	delete_dir(dir_path)
		self.clean()
		
if __name__ == '__main__':
	print 'SpiderController.py'
	localURL        = r'f:\\Test'
	dirName         = r'shiyan'
	startPage       = 'http://iie.ac.cn/'
	checker_ip      = '127.0.0.1'
	checker_port    = 1234
	redis_ip        = '10.10.41.45'
	redis_port      = 6379
	task_descriptor = '{"dirname":"shiyan"}'
	controller = SpiderController()
	controller.set_localURL(localURL, dirName) #设置本地保存数据的路径
	controller.init_dir() #创建保留数据的本地目录
	controller.get_task(startPage) #获得任务,即要扫描的网址
	controller.init_spiders(Num_Of_URLSpider = 25, timeout1 = 10, #URLSpider线程数和网络延迟等待时间
							Num_Of_DownloadSpider = 20, timeout2 = 10, #DownloadSpider线程数和网络延迟等待时间
							ip1 = checker_ip, port1 = checker_port, #Sender配置
							ip2 = redis_ip, port2 = redis_port, 
							descriptor = task_descriptor) 
	controller.wait_for_end() #等待全部线程结束
	controller.save_and_exit() #退出并保存结果
	
