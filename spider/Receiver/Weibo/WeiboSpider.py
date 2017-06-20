# -*- coding:utf-8 -*-
# Python2.7.12

from WeiboLogin import *
from spider.Tools.Find_Path import find_json_file
from Queue import Queue
import json
import traceback
import re
import os
import md5
import urlparse
import time
import threading
import posixpath

def read_setting_from_json(rel_path):
	try:
		f = open(rel_path, 'r')
		content = f.read()
		f.close()
	except:
		print 'Can not open json file:', rel_path
	dict = json.loads(content)
	userName = dict['userName']
	passWord = dict['passWord']
	return userName, passWord

#url拼接
def urljoin(base, url):	
	url = urlparse.urljoin(base, url)
	url = url.replace('../', '')
	return url
	
# get md5 value of data
def get_md5(data):
	data = str(data)
	return md5.new(data).hexdigest()
	
def save_file(dir, content):
	try:
		f = open(dir, 'w+')
		f.write(content)
		f.close() 
	except:
		print 'can not create file:', dir
		return False
	else:
		print 'success create a file: ', dir
		return True
		
class WeiboSpider(threading.Thread):
	articleURL = ''
	pageURL    = ''
	Lock       = threading.RLock() #Lock for Total
	Total      = 0
	allThread  = []
	taskQueue  = Queue()
	
	#重置
	@staticmethod
	def Reset():
		WeiboSpider.articleURL = ''
		WeiboSpider.pageURL    = ''
		WeiboSpider.Total      = 0
		WeiboSpider.allThread  = []
		WeiboSpider.taskQueue  = Queue()
		
	#计数加一
	@staticmethod
	def Add_Num():
		WeiboSpider.Lock.acquire()
		WeiboSpider.Total += 1
		WeiboSpider.Lock.release()
		
	#判断是否所有线程都已没有任务；如果是，返回True
	@staticmethod
	def AllThreadEnd():
		for thread in WeiboSpider.allThread:
			if thread.status == False:
				return False
		return True
		
	def __init__(self, senderQueue):
		threading.Thread.__init__(self)
		self.senderQueue = senderQueue
		self.status      = False
		self.articleDir  = WeiboSpider.articleURL
		self.pageDir     = WeiboSpider.pageURL
		
	def login(self, userName, passWord):
		self.weibo = WeiboLogin(userName, passWord)
		return self.weibo.Login()
	
	def get_task(self):
		task = WeiboSpider.taskQueue.get()
		return task
	
	# 通过公众号首页获得公众号id
	def get_id(self, content):
		p = re.compile('\$CONFIG\[\'oid\'\].?=\'(.*?)\'')
		id = p.search(content).group(1)
		return id
	
	def get_pid(self, content):
		p = re.compile('\$CONFIG\[\'page_id\'\].?=\'(.*?)\'')
		pid = p.search(content).group(1)
		return pid
	
	def get_wenzhang_url(self, content):
		pid = self.get_pid(content)
		url = 'http://weibo.com/p/%s/wenzhang' %(pid) 
		return url
		
	def get_img_url(self, content):
		pid = self.get_pid(content)
		url = 'http://weibo.com/p/%s/photos?from=profile_right#wbphoto_nav' %(pid)
		return url
		
	def download(self, url):
		try:
			content = self.weibo.opener.open(url).read()
		except:
			traceback.print_exc()
			return None
		else:
			return content

	def save_article(self, content):
		fileName = get_md5(content) + '.html'
		status = save_file(self.articleDir + '\\' + fileName, content)
		return status
	
	def save_page(self, content):
		fileName = get_md5(content) + '.html'
		status = save_file(self.pageDir + '\\' + fileName, content)
		return status
	
	def send_msg(self, task_content):
		self.senderQueue.put(task_content)
	
	def download_articles_from_list_page(self, url):
		try:
			parentURL = url
			content   = self.download(url)
			if content == None:
				return False
			parent_id  = get_md5(content)
			#self.save_page(content)
			print 'get url:', url
			#time.sleep(1)
			if content == None:
				return False
			reStr = r'<a target=\\\"_blank\\\" href=\\\"(.*?)=zwenzhang\\\"'
			articleList = re.findall(reStr, content)
			articleSet = set()
			for url in articleList:
				if url not in articleSet:
					articleSet.add(url)
					url = url.replace('\\', '') + '=zwenzhang'
					url = urljoin(parentURL, url)
					print 'article url: ', url
					articleContent = self.download(url)
					self.save_article(articleContent)
					hash  = get_md5(articleContent)
					rel_path    = self.articleDir + '\\' + hash + '.html'
					task_content = {}
					task_content['title']     = 'No Title'
					task_content['parent_id'] = parent_id
					task_content['web_url']   = url
					task_content['file_url']  = url
					task_content['rel_path']  = rel_path
					task_content['hash']      = hash
					self.send_msg(task_content)
					WeiboSpider.Add_Num()
					#time.sleep(1)
			reStr = r'class=\\\"page next S_txt1 S_line1\\\" href=\\\"(.*?)\\\"'
			try:
				result = re.findall(reStr, content)
				if len(result) == 0:
					return True
				url = result[0].replace('\\', '')
				nextArticleList = urljoin(parentURL, url)
			except:
				nextArticleList = None
				return False
			else:
				self.download_articles_from_list_page(nextArticleList)
		except:
			traceback.print_exc()
			return False
		else:
			return True
		
	def run(self):
		try:
			jsonPath = find_json_file('..\\weibo.json')
			userName, passWord = read_setting_from_json(jsonPath)
			status = self.login(userName, passWord)
			if status == False:
				print 'Login Error!'
			else:
				task = self.get_task()
				content = self.download(task)
				articleUrl = self.get_wenzhang_url(content)
				self.download_articles_from_list_page(articleUrl)
		except:
			traceback.print_exc()
		self.status = True
