# -*- coding:utf-8 -*-
# Python2.7.12
import env
from Queue import Queue
import json
import traceback
import re
import os
import md5
import urlparse
import threading
import hashlib
import urllib2
import binascii
import httplib2
import zlib
import time
from bs4 import BeautifulSoup
import sys	

class data_table:
    def __init__(self, rel_path = '', hash = '', title = '', parent_id = '', web_url = '', file_url = ''):
        self.rel_path = rel_path
        self.hash = hash
        self.title = title
        self.parent_id = parent_id
        self.web_url = web_url
        self.file_url = file_url

    def get_dict(self):
        return {
				'rel_path': self.rel_path, 
				'hash': self.hash, 
				'title': self.title, 
				'parent_id': self.parent_id,
                'web_url': self.web_url, 
				'file_url': self.file_url
				}

def get_md5(obj):
    md = hashlib.md5()
    md.update(obj)
    return md.hexdigest()

class WeixinSpider(threading.Thread):
	articleURL    = ''
	imgURL        = ''
	Article_Lock  = threading.RLock() # Lock for Article_Total
	Image_Lock   = threading.RLock() # Lock for Image_Total
	Article_Total = 0
	Image_Total   = 0
	allThread     = []
	taskQueue     = Queue()
	
	# 重置
	@staticmethod
	def Reset():
		WeixinSpider.articleURL    = ''
		WeixinSpider.imgURL        = ''
		WeixinSpider.Article_Total = 0
		WeixinSpider.Image_Total   = 0
		WeixinSpider.allThread     = []
		WeixinSpider.taskQueue     = Queue()
		
	# aticle计数加一
	@staticmethod
	def Add_Article_Total():
		WeixinSpider.Article_Lock.acquire()
		WeixinSpider.Article_Total += 1
		WeixinSpider.Article_Lock.release()
	
	# image计数加一
	@staticmethod
	def Add_Image_Total():
		WeixinSpider.Image_Lock.acquire()
		WeixinSpider.Image_Total += 1
		WeixinSpider.Image_Lock.release()
		
	# 判断是否所有线程都已没有任务；如果是，返回True
	@staticmethod
	def AllThreadEnd():
		for thread in WeixinSpider.allThread:
			if thread.status == False:
				return False
		return True
		
	def __init__(self, senderQueue):
		threading.Thread.__init__(self)
		self.senderQueue = senderQueue
		self.status      = False
		self.articleDir  = WeixinSpider.articleURL
		self.imgDir     = WeixinSpider.imgURL
		print 'imgDir is: ', self.imgDir
		
	def get_task(self):
		task = WeixinSpider.taskQueue.get()
		return task
		
	def send_msg(self, task_content):
		self.senderQueue.put(task_content)

		
	def get_urls(self, key):
		import sys
		reload(sys)
		sys.setdefaultencoding('utf-8')
		from selenium import webdriver
		urls = []
		titles = []
		try:
			driver = webdriver.Chrome()
		except:
			print 'can not use the chrome driver.'
			return [urls, titles]
		try:
			driver.get('http://weixin.sogou.com/')
			wechat_num = unicode(key)
			driver.find_element_by_id("upquery").send_keys(wechat_num)
			driver.find_element_by_class_name("swz2").click()
			now_handle = driver.current_window_handle
			driver.find_elements_by_class_name('img-box')[0].click()
			time.sleep(10)
			
			for handle in driver.window_handles:
				if handle != now_handle:
					driver.switch_to_window(handle)
					
			for i in range(0, len(driver.find_elements_by_class_name('weui_media_hd'))):
				driver.find_elements_by_class_name('weui_media_hd')[i].click()
				urls.append(driver.current_url)
				titles.append(driver.title)
				driver.back()
		except:
			print 'can not use the chrome driver.'
		finally:
			driver.quit()
		
		return [urls, titles]	
		
	def get_datas_from_url(self, page_url, title):
		h = httplib2.Http()
		request = urllib2.Request(page_url)
		request.add_header('Accept-encoding', 'gzip')
		opener = urllib2.build_opener()
		response = opener.open(request)
		
		html = response.read()
		gzipped = response.headers.get('Content-Encoding')
		if gzipped:
			html = zlib.decompress(html, 16 + zlib.MAX_WBITS)
		content = html
		
		page = data_table()
		page.title     = title
		page.web_url   = page_url
		page.file_url  = page_url
		page.hash      = get_md5(content)
		page.parent_id = page.hash		
		page_filename  = self.articleDir + '\\' + page.hash + '.html'
		page.rel_path  = page_filename
		# save as file
		open(page_filename, 'wb').writelines(content)
		WeixinSpider.Add_Article_Total()
		# send msg to Sender
		msg = page.get_dict()
		self.send_msg(msg)
		
		print unicode(title) + u' Html download end.'
		
		matchmsg_cdn_url = re.search(r'var\s*msg_cdn_url\s*=\s*[\'\"](?P<msg_cdn_url>\S*)[\'\"];', content)
		msg_cdn_url = matchmsg_cdn_url.group('msg_cdn_url')
		face_url = msg_cdn_url
		resp, contentface = h.request(face_url)
		print '**********' + u'downloading surface：' + face_url + '**********'
		
		face = data_table()
		face.title     = title
		face.web_url   = page_url
		face.parent_id = page.hash
		face.file_url  = face_url
		face.hash      = get_md5(contentface)
		file_name      = self.imgDir + '\\' + face.hash + '.jpg'
		face.rel_path  = file_name
		# save jpg
		open(file_name, 'wb').write(contentface)
		WeixinSpider.Add_Image_Total()
		# send msg to Sender
		msg = face.get_dict()
		self.send_msg(msg)
		
		soup = BeautifulSoup(content, 'html.parser')
		for link in soup.find_all('img'):
			if None != link.get('data-src'):
				orurl = link.get('data-src')
				url = orurl.split('?')[0]
				resp, content = h.request(url)
				print u'download：' + url
				
				matchurlvalue = re.search(r'wx_fmt=(?P<wx_fmt>[^&]*)', orurl)
				if None != matchurlvalue:
					wx_fmt = matchurlvalue.group('wx_fmt')
				else:
					wx_fmt = binascii.b2a_hex(content[0:4])
				phototype = {
							'jpeg': '.jpg', 
							'gif': '.gif', 
							'png': '.png', 
							'jpg': '.jpg', 
							'47494638': '.gif',
							'ffd8ffe0': '.jpg', 
							'ffd8ffe1': '.jpg', 
							'ffd8ffdb': '.jpg', 
							'89504e47': '.png'
							}
				image = data_table()
				image.title     = title
				image.web_url   = page_url
				image.parent_id = page.hash
				image.file_url  = url
				image.hash      = get_md5(content)
				file_name = self.imgDir + '\\' + image.hash + phototype[wx_fmt]
				image.rel_path = file_name
				# save img
				open(file_name, 'wb').write(content)
				WeixinSpider.Add_Image_Total()
				# send msg to Sender
				msg = image.get_dict()
				self.send_msg(msg)
				
		print '**********' + unicode(title) + u' image download end' + '**********'	
		
	def run(self):
		try:
			task = self.get_task()
			print 'task is:', task
			url_title = self.get_urls(task)
			for i in range(len(url_title[0])):
				self.get_datas_from_url(url_title[0][i], url_title[1][i])
		except:
			traceback.print_exc()
		self.status = True