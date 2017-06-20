# -*- coding:utf-8 -*-
# 作用: 具体的爬虫实现
# 运行环境: Python2.7

import threading
import urllib2
import md5
import HTMLParser
import re
import StringIO
import sys
import os
import traceback
import urlparse
import time
import gzip
import posixpath
from Queue import Queue
reload(sys)
sys.setdefaultencoding('utf-8')
DONE = 2 #表示已完成

#获得data的md5值
def get_md5(data):
	data = str(data)
	return md5.new(data).hexdigest()

#url拼接
def urljoin(base, url):	
	url = urlparse.urljoin(base, url)
	url = url.replace('../', '')
	url = url.replace('/?', '?')
	return url

#存储MD5值的新List
class NewMd5List(list):
	def __init__(self):
		list.__init__(self)
		self.Lock = threading.RLock() #Lock for insert
	
	#删除掉列表中的元素
	def delete(self, num):
		num = get_md5(num)
		if num in self:
			self.remove(num)
	
	#将data的md5值插入列表中
	def inset_by_md5(self, num):
		self.Lock.acquire()	
		result = self.__find_by_md5(num)
		num = get_md5(num)
		if not result[0]:
			self.insert(result[1], num)
			self.Lock.release()
			return True
		else:
			self.Lock.release()
			return False
		
	#输入data的md5值已存于list中返回:True,位置；否则返回:False，应当插入的位置
	def __find_by_md5(self, num):
		num = get_md5(num)
		result = self.__find(num)
		return result
		
	#找到num在列表中的位置
	def __find(self, num):
		l = len(self)
		first = 0
		end = l - 1
		mid = 0
		if l == 0 or num < self[first]:
			return False, 0
		elif num > self[end]:
			return False, end + 1
		while first <= end:
			mid = (first + end)/2
			if num < self[mid]:
				end = mid - 1
			elif num > self[mid]:
				first = mid + 1
			else:
				return True, mid
		if num < self[mid]:
			return False, mid
		else:
			return False, mid + 1
	
#文档记录器，对文档进行相应操作	
class Recorder():
	#创建文件fileName，并写入数据data
	def write(self, fileName, data):
		try:
			fileWriter =open(fileName, 'wb')
			fileWriter.write(data)
			fileWriter.close()
		except:
			traceback.print_exc()
			print 'recorder: error in write %s' %(fileName)
			return False
		return True
		
	#向conf文件中写入记录
	def write_in_conf(self, confName, task_content, Lock = None):
		try:
			if Lock != None:
				Lock.acquire()
			fileWriter = open(confName, 'a')
			for key in task_content:
				fileWriter.write(key + ': ' + task_content[key] + '\n')
			fileWriter.close()
			if Lock != None:
				Lock.release()
		except:
			traceback.print_exc()
			print 'recorder: error in write_in_conf'
			return False
		return True

#网页内容分析器
class WebParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.urlList = []
		
	def reset(self):
		self.urlList = []
		HTMLParser.HTMLParser.reset(self)
	
	#返回网页主题
	def get_title(self, data):
		title = ''
		titleList = re.findall(r'<title>([\s\S]+?)</title>', data)
		if len(titleList) > 0:
			title = titleList[0]
		if title == None or title == '':
			title = 'No title'
		try:
			title = title.decode('utf-8')
		except:
			try:
				title = title.decode('gbk')
			except:
				title = 'No title'
		title = title.encode('utf-8')
		return title.strip() #删除空白符
	
	#获得文件的title
	def get_file_title(self, fileName, data):
		title = ''
		fileName = fileName.replace('(', r'\(')
		fileName = fileName.replace(')', r'\)')
		regx1 = r'href=.*' + fileName + r'.*>([^>"]+?[^<"])"?</a>'
		titleList = re.findall(regx1, data)
		for item in titleList:
			title = item
		if title == None or title == '':
			title = 'No title'
		try:
			title = title.decode('utf-8')
		except:
			try:
				title = title.decode('gbk')
			except:
				pass
		title = title.encode('utf-8')
		return title.strip() #删除空白符
		
	#分析网页获得网页、文档、图片的超链接		
	def handle_starttag(self, tag, attrs):
		if tag == 'a' or tag == 'img':
			for name, value in attrs:
				if name == 'href' or name == 'src':
					self.urlList.append(value)
	
	
	def search_URL(self, data):
		regx = r'<a href="(.+?)"'
		urlList = []
		try:
			urlList = re.findall(regx, data)
		except: #编码问题
			pass
			
		return urlList
	
	#获得网页中的超链接(作为handle_starttag的补充)
	def get_URL(self, data):
		urlList = self.search_URL(data)
		for item in urlList:
			if not item in self.urlList:
				self.urlList.append(item)
				
	def smart_parse_start_page(self, data):
		urlList = self.search_URL(data)
		map = {}
		num = len(urlList)
		result = []
		for url in urlList:
			tumple = urlparse.urlparse(url) #解析url成分
			url = tumple.netloc #根域
			regx = re.compile('.*\.([a-zA-Z]+\.[a-zA-Z]+).*')
			url = re.findall(regx, url)
			if (len(url) == 0):
				continue
			url = url[0]
			if url not in map:
				map[url] = 1
			else:
				map[url] += 1
		if num > 0:
			for url in map:
				if map[url]*1.0/num > 0.3:
					result.append(url)
		
		return result
	
#根据URL分析相应的信息		
class URLParser():
	#判断是否为文件	
	def isFile(self, url):
		if os.path.splitext(url)[1] == '':	
			return False
		return True
	
	#输入文件绝对或相对路径，输出文件类型
	def get_file_type(self, url):
		return os.path.splitext(url)[1]
		
	# 输入文件的绝对路径，输出文件所在的目录地址
	def get_dir(self, url):
		fileName = os.path.basename(url)
		dir = url[:-len(fileName)]
		return dir
	
	# 通过url获得文件名
	def get_file_name(self, url):
		return os.path.basename(url)
		
# 下载网页并解析出URL
class URLSpider(threading.Thread):
	queue       = Queue()
	localURL    = '' # 本地保存下载内容的文件夹路径
	dataList    = NewMd5List() #避免下载重复的页面内容
	urlList     = NewMd5List() #避免保存重复的url
	Total       = 0 #总共成功分析过的网页数
	totalLock   = threading.RLock() #对Total加锁
	confLock    = threading.RLock() #对conf.txt
	domainList  = [] #检查的域列表
	allThread   = [] #所有URLSpider的列表
	webTypes    = [	'.net', '.com', '.cn', '.html', '.htm'
					'.shtml', '.top', '.org', '.gov', '.edu'
					'.cn', '.aero', ''] #需要''，因为有的网页没有后缀名
	
	#重置
	@staticmethod
	def Reset():
		URLSpider.queue      = Queue()
		URLSpider.localURL   = '' #本地保存下载内容的文件夹路径
		URLSpider.dataList   = NewMd5List() #避免下载重复的页面内容
		URLSpider.urlList    = NewMd5List() #避免保存重复的url
		URLSpider.Total      = 0 #总共成功分析过的网页数
		URLSpider.domainList = [] #检查的域列表
		URLSpider.allThread  = [] #所有URLSpider的列表
	
	#判断是否所有线程都已没有任务；如果是，返回True
	@staticmethod
	def AllThreadEnd():
		for thread in URLSpider.allThread:
			if thread.status == False:
				return False
		return True

	#分析成功的网页总数增加1，将来应实时发送给展示方
	@staticmethod
	def AddTotal():
		URLSpider.totalLock.acquire()
		URLSpider.Total += 1 
		URLSpider.totalLock.release()
	
	def __init__(self, spiderName, senderQueue, timeout = 20, rank = 0x7fffffff):
		threading.Thread.__init__(self, name = spiderName)
		self.kill         = False
		self.recorder     = Recorder() #文档记录器
		self.URLParser    = URLParser() #url分析器
		self.WebParser    = WebParser() #网页内容分析器
		self.status       = False #当前状态，True表示准备退出
		self.timeout      = timeout #设置超时时间
		self.rank       = rank #设置检查层级
		self.senderQueue  = senderQueue
		self.opener       = urllib2.build_opener() # gzip下载使用
		
	#显示当前任务数
	def show_current_task_num(self):
		taskNum = URLSpider.queue.qsize()
		print '%s: current task number is %d' %(self.name, taskNum)
		
	#给网页命名一个本地保存的文件名
	def get_saved_name(self, url, data):
		fileType = self.URLParser.get_file_type(url)
		if fileType != '.shtml' and fileType != '.htm':
			fileType = '.html'
		savedName = URLSpider.localURL + '\\' + get_md5(data) + fileType
		return savedName
		
	#保存网页内容
	def save_web(self, url, data):
		fileName = self.get_saved_name(url, data)
		return self.recorder.write(fileName, data)
	
	#将下载的数据放入Sender的任务队列
	def send_msg(self, task_content):
		self.senderQueue.put(task_content) 
		
	#设置当前线程的状态，当前任务队列为空时，设置为True
	def set_status(self, status):
		self.status = status
		
	#将网页信息写入conf.txt，同时通信发送给检查方	
	def write_and_send_msg(self, parent_id, url, data):
		title    = self.WebParser.get_title(data)
		confURL  = URLSpider.localURL + '\\' + 'conf.txt'
		hash     = get_md5(data)
		localURL =  self.get_saved_name(url, data) 
		task_content    = {}
		task_content['title']     = title # 网页的主题
		task_content['parent_id'] = parent_id # 网页父链接
		task_content['web_url']   = url # 网页的url
		task_content['file_url']  = url # 所在网页的url（对于网页而言值相同）
		task_content['rel_path']  = localURL # 保存在本地的名称
		task_content['hash']      = hash # 网页内容的md5值
		self.send_msg(task_content) # 放入Sender的任务队列
		self.recorder.write_in_conf(confURL, task_content, URLSpider.confLock) # 记录到conf
	
	def smart_parse_start_page(self, data):
		web_parser = WebParser()
		result = web_parser.smart_parse_start_page(data)
		return result
	
	#判断当前链接是否在检查域内
	def isInDomain(self, url):
		for item in URLSpider.domainList:
			try:
				if item in url:
					return True
			except:
				return False
		return False
		
	#分析网页获得网页、文档、图片的超链接
	def get_URLs(self, webURL, data):
		urlList = []
		parser = WebParser()
		try:
			parser.feed(data)
		except:
			return urlList
		parser.get_URL(data) #对feed函数进行补充，feed获得url能力不足
		for url in parser.urlList:
			url1 = urljoin(webURL, url)
			if self.isInDomain(url1): #域内且未检测过的链接
				if URLSpider.urlList.inset_by_md5(url1):
					urlList.append(url1)
		return urlList
	
	#对所有超链接归类，并放入对应的任务队列中
	def classify(self, parent_id, parent_url, urlList, parentData, rank):
		for url in urlList:
			fileType = self.URLParser.get_file_type(url)
			if fileType in URLSpider.webTypes or 'htm' in fileType: #是一个网页链接
				URLSpider.queue.put((parent_id, url, rank+1))
			else: #要下载的文档或图片链接
				title  = None
				fileType = self.URLParser.get_file_type(url).lower()
				if fileType in DownloadSpider.fileTypes: #如果是文档
					fileName = self.URLParser.get_file_name(url) #获得文档名
					title  = self.WebParser.get_file_title(fileName, parentData) #获得文档的title
					if title == None:
						title = 'No Title'
				elif fileType in DownloadSpider.imgTypes: #如果是图片
					title = 'No Title'
				else:
					continue
				DownloadSpider.queue.put((parent_id, parent_url, url, title))
	
	#分析一个网页的内容
	def parse_one_URL(self, parent_id, url, rank):
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0')
			page = urllib2.urlopen(request, None, self.timeout)
		except: 
			if parent_id == None:
				print 'Can not get startPage:%s and try again.' %(url)
				URLSpider.queue.put(('None', url, 0)) #try again
				time.sleep(1)
			return False
		try:
			#print 'page.read'
			if page.code == 200:
				#charset_info = page.info.getheader('Content-Type')
				data = page.read()
				#print 'page.read end'
		except:
			page.close()
			#print 'can not read web'
			return False
		page.close()
		# if is the start page
		if parent_id == None:
			domains = self.smart_parse_start_page(data)
			for domain in domains:
				URLSpider.domainList.append(domain)
		
		URLSpider.urlList.inset_by_md5(url) #加入成功下载的url列表中
		if not URLSpider.dataList.inset_by_md5(data): #保存页面成功，记录避免重复下载
			return DONE
		if not self.save_web(url, data): #保存页面
			URLSpider.dataList.delete(data)
			return False
		#成功下载的网页总数增加1，将来应实时发送给展示方
		URLSpider.AddTotal()
		if parent_id == None:
			parent_id = get_md5(data)
		self.write_and_send_msg(parent_id, url, data) #保存网页的信息到conf.txt文件,并发送msg
		urlList = self.get_URLs(url, data) #获得网页中的所有超链接
		current_id = get_md5(data) #计算本网页的hash值，作为子连接的父hash
		self.classify(current_id, url, urlList, data, rank) #对所有超链接归类，并放入对应的任务队列中
		return True
	
	#获取网页url，并分析
	def run(self):
		try:
			while True:
				if self.kill:
					break
				try:
					tumple = URLSpider.queue.get(True, 1)
				except:
					tumple = None
				if tumple == None: #当任务数量为0
					self.set_status(True)
					if URLSpider.AllThreadEnd(): #如果所有线程都没有任务了就退出
						break
				else:
					self.set_status(False) #获得任务，设置当前状态为有任务
					# if self.name == ('URLSpider' + str(0)): #显示当前任务数
						# self.show_current_task_num() 
					parent_id = tumple[0] #父id
					url = tumple[1] #当前链接
					rank = tumple[2] #层级
					try:
						if rank > self.rank:
							break
						success = self.parse_one_URL(parent_id, url, rank) #下载一个页面并分析
					except:
						traceback.print_exc()
						print 'URLSpider:Error in parse:', url
						continue
					if not success:
						pass #记录下分析失败的url
					elif success == DONE:
						pass #该页面之前分析过
		except:
			traceback.print_exc()
			print 'URLParser: Error in the thread: ', self.name
		finally:
			#print '%s exit！' %(self.name)
			self.set_status(True)
			return True
		
#下载图片和文件
class DownloadSpider(threading.Thread):
	queue     = Queue() #任务队列
	imgNum    = 0 #下载的图片数量
	fileNum   = 0 #下载的文档数量
	dataList  = NewMd5List() #防止下载重复的数据
	imgTypes  = ['.jpg', '.png', '.gif', '.bmp', '.dib', '.tif'] #图片类型列表
	fileTypes = ['.doc', '.xls', '.docx', '.xlsx', '.pptx',     #文档类型列表
				'.zip', '.xml', '.txt', '.pdf', '.rar',
				'.et', '.pps', '.pps', '.rtf', '.ppt', 
				'.dps', '.wps', '.7z', '.ios']
	imgLocalURL  = '' #本地保存下载图片的文件夹路径
	fileLocalURL = '' #本地保存下载文件的文件夹路径
	imgNumLock   = threading.RLock() #Lock for imgNum
	fileNumLock  = threading.RLock() #Lock for fileNum
	imgConfLock  = threading.RLock() #Lock for imgConf
	fileConfLock = threading.RLock() #Lock for fileConf
	allThread    = [] #所有DownloadSpider的列表
	
	#重置
	@staticmethod
	def Reset():
		DownloadSpider.queue        = Queue() #任务队列
		DownloadSpider.imgNum       = 0 #下载的图片数量
		DownloadSpider.fileNum      = 0 #下载的文档数量
		DownloadSpider.dataList     = NewMd5List() #防止下载重复的数据
		DownloadSpider.imgLocalURL  = '' #本地保存下载图片的文件夹路径
		DownloadSpider.fileLocalURL = '' #本地保存下载文件的文件夹路径
		DownloadSpider.allThread    = [] #所有DownloadSpider的列表
	
	#判断是否所有线程都已没有任务，如果是，返回True
	@staticmethod
	def AllThreadEnd():
		for thread in DownloadSpider.allThread:
			if thread.status == False:
				return False
		return True
	
	#下载的图片数增加一
	@staticmethod
	def AddImgNum():
		DownloadSpider.imgNumLock.acquire()
		DownloadSpider.imgNum += 1
		DownloadSpider.imgNumLock.release()	
	
	#下载的文档数增加一
	@staticmethod
	def AddFileNum():
		DownloadSpider.fileNumLock.acquire()
		DownloadSpider.fileNum += 1
		DownloadSpider.fileNumLock.release()		
	
	def __init__(self, spiderName, senderQueue, timeout = 20):
		threading.Thread.__init__(self, name = spiderName)
		self.kill         = False
		self.recorder     = Recorder() #文档记录器
		self.URLParser    = URLParser() #url分析器
		self.WebParser    = WebParser() #网页内容分析器
		self.timeout      = timeout #设置超时时间
		self.status       = False #当前状态，True时表示等待退出
		self.opener       = urllib2.build_opener() # 下载文件与图片专用
		self.senderQueue  = senderQueue
		
	#显示当前任务数
	def show_current_task_num(self):
		taskNum = DownloadSpider.queue.qsize()
		print '%s: current file task number is %d' %(self.name, taskNum)	
	
	#给数据命名一个本地保存的文件名,本地存储文件夹路径，web链接，数据
	def get_saved_name(self, localURL, url, data):
		fileType = self.URLParser.get_file_type(url) #获得文件类型
		savedName = localURL + '\\' + get_md5(data) + fileType
		return savedName
	
	#保存数据内容
	def save_data(self, localURL, url, data):
		fileName = self.get_saved_name(localURL, url, data)
		return self.recorder.write(fileName, data)
	
	#将下载的数据放入Sender的任务队列
	def send_msg(self, task_content):
		self.senderQueue.put(task_content) 
	
	#设置当前线程的状态，退出时设置为True
	def set_status(self, status):
		self.status = status
		
	#下载url链接的内容
	def download(self, url):
		data = None
		try:
			#print 'urlopen'
			request = urllib2.Request(url)
			request.add_header('Accept-encoding', 'gzip')
			request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0')
			page = self.opener.open(request)
			#page = urllib2.urlopen(url, None, self.timeout)
			#print 'urlopen end', self.timeout
		except:
			#print 'can not get file:%s' %(url)
			return False, None
		try:
			#print 'page.read'
			if page.code == 200:
				predata = page.read()
				pdata   = StringIO.StringIO(predata)
				gzipper = gzip.GzipFile(fileobj = pdata)
				try:
					data = gzipper.read()
				except:
					data = predata
			#print 'page.read end'
		except:
			traceback.print_exc()
			page.close()
			return False, None
		page.close()
		return True, data
		
	#写入conf,dir:conf所在的路径，parent_id父页面的链接，url:本页面的链接，data:数据，title:标题
	def write_and_send_msg(self, dir, parent_id, web_url, url, data, title):
		confURL      = dir + '\\' + 'conf.txt' #获得conf路径
		fileName     = self.URLParser.get_file_name(url) #获得文档名
		localURL     = self.get_saved_name(dir, url, data) #获得保存到本地的文件路径
		hash         = get_md5(data)
		task_content = {}
		task_content['title']     = title
		task_content['parent_id'] = parent_id
		task_content['web_url']   = web_url
		task_content['file_url']  = url
		task_content['rel_path']  = localURL
		task_content['hash']      = hash
		self.send_msg(task_content) #将下载的数据放入Sender的任务队列
		self.recorder.write_in_conf(confURL, task_content, DownloadSpider.fileConfLock) #记录到conf
		
	#下载一个文件,dir:保存在本地的地址
	def task(self, dir, parent_id, web_url, url, title):
		success, data = self.download(url) #下载链接的内容
		
		if success: #下载成功
			if not DownloadSpider.dataList.inset_by_md5(data): #该文件已下载过:否，则加入
				return DONE
			if not self.save_data(dir, url, data): #保存文件，文件名是data的md5值
				DownloadSpider.dataList.delete(data) #未成功下载，删除下载记录
				return False
			self.write_and_send_msg(dir, parent_id, web_url, url, data, title) #写入conf.txt中
			return True
		else:
			return False
		
	#完成一个任务事项
	def do_one_task(self, parent_id, web_url, url, title):
		status = False #标记任务是否顺利完成
		fileType = self.URLParser.get_file_type(url).lower() #获得文件类型

		if fileType in DownloadSpider.fileTypes: #文本文件
			dir = DownloadSpider.fileLocalURL #conf所在目录的路径
			status   = self.task(dir, parent_id, web_url, url, title)
			if status == True:
				DownloadSpider.AddFileNum()
			pass
		else: #图片文件
			dir = DownloadSpider.imgLocalURL #conf所在目录的路径
			status   = self.task(dir, parent_id, web_url, url, title)
			if status == True:
				DownloadSpider.AddImgNum()
		return status
			
	def run(self):
		try:
			while True:
				if self.kill:
					break
				try:
					tumple = DownloadSpider.queue.get(True, 1)
				except:
					if URLSpider.AllThreadEnd(): #URLSpider所有线程结束
						break
				else:
					# if self.name == ('DownloadSpider' + str(0)): #显示当前任务数
						# self.show_current_task_num()
					parent_id = tumple[0] #父链接id
					web_url   = tumple[1] #所在的网页链接
					url       = tumple[2] #自身的下载超链接
					title     = tumple[3] #文档title，图片的title默认为'No Title'
					try:
						success = self.do_one_task(parent_id, web_url, url, title) #完成一个任务事项
					except:
						traceback.print_exc()
						print 'DownloadSpider:Error in run do_one_task:', url
						continue
					if not success:
						pass #记录下分析失败的url
					elif success == DONE:
						pass #该页面之前分析过
		except:
			traceback.print_exc()
			print 'DownloadSpider:Error in the thread: ', self.name
		finally:
			#print '%s exit！' %(self.name)
			#设置状态为退出
			self.set_status(True)
			return True
		
		
		
