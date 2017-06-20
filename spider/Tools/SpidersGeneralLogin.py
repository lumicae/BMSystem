# Python 2.7.12
# -*- coding:utf-8 -*-
# 注：未完成，因为需求不明，所以暂时写了，但是没有用上。（可能会用到内网的检测）
import re
import md5
import urllib
import cookielib
import urllib2
from PIL import Image
import cStringIO
import json
import threading
import pytesseract

# _opener = None

class SingletonOpener(object):
	__mutex = threading.Lock()
	instance = None
	
	def __init__(self):
		cookieJar = cookielib.LWPCookieJar()
		cookie_support = urllib2.HTTPCookieProcessor(cookieJar)
		self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
	
	def __new__(self):
		if (SingletonOpener.instance == None):
			SingletonOpener.__mutex.acquire()
			if (SingletonOpener.instance == None):
				SingletonOpener.instance = object.__new__(self)
			SingletonOpener.__mutex.release()
		return SingletonOpener.instance

def read_name_and_password(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		return setting

def md5_value(content):
	content = str(concent)
	return md5.new(content).hexdgest()
	
def init_opener():
	Opener = SingletonOpener()

	return Opener.opener
	
def get_img(opener, img_url):
	request = opener.open(img_url)
	img_data = request.read()
	print img_data
	image = Image.open(cStringIO.StringIO(img_data))
	image.show()
	return image
	
def get_postData(file_path, certCode):
	setting = read_name_and_password(file_path)
	postData = {
		'userName': setting['username'],
		'pwd': setting['password'],
		'certCode': certCode,
		'sb': 'sb'
	}
	print postData
	return urllib.urlencode(postData)
	
def init_login(log_url, json_path, check_url = None):
	opener = init_opener()
	'''
	# identifying code
	image = get_img(opener, check_url)
	# certCode = raw_input()
	certCode = pytesseract.image_to_string(image)
	print certCode
	'''
	postData = get_postData(json_path, certCode)
	postHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'}
	request = urllib2.Request(log_url, postData, postHeader)
	result = opener.open(request)
	
	urllib2.install_opener(opener)
	#return opener
	
if __name__ == '__main__':
	# opener = init_opener()
	# img_url = 'http://sep.ucas.ac.cn/changePic'
	# image = get_img(opener, img_url)
	# certCode = pytesseract.image_to_string(image)
	
	opener = init_opener()
	img_url = 'http://sep.ucas.ac.cn/changePic'
	image = get_img(opener, img_url)
	#certCode = raw_input()
	certCode = pytesseract.image_to_string(image)
	certCode = str(certCode)
	print 'hello'
	print certCode
	print 'hello'
	postData = get_postData('f:\\setting.json', certCode)
	postHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'}
	request = urllib2.Request('http://sep.ucas.ac.cn/slogin', postData, postHeader)
	result = opener.open(request)
	get_img(opener, img_url)
	certCode = raw_input()
	certCode = str(certCode)
	print certCode
	postData = get_postData('f:\\setting.json', certCode)
	request = urllib2.Request('http://sep.ucas.ac.cn/slogin', postData, postHeader)
	result = opener.open(request)
	text = result.read()
	fin = open('f:\\text.html', 'wb')
	fin.write(text)
	fin.close()
	# print text
	