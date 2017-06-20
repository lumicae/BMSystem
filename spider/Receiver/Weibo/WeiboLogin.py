#Python2.7.12
# -*- coding:utf-8 -*-

import urllib2
import cookielib
import traceback
import re
import json
import urllib
import rsa
import base64
import binascii

def PostEncode(userName, passWord, serverTime, nonce, pubkey, rsakv):
	encodedUserName = GetUserName(userName)
	encodePassWord = get_pwd(passWord, serverTime, nonce, pubkey)
	postData = {
		'entry':'weibo',
		'gateway':'1',
		'from':'',
		'savestate':'7',
		'userticket':'1',
		'ssosimplelogin':'1',
		'vsnf':'1',
		'vsnval':'',
		'su':encodedUserName,
		'service':'miniblog',
		'servertime':serverTime,
		'nonce':nonce,
		'pwencode':'rsa2',
		'sp':encodePassWord,
		'encoding':'UTF-8',
		'prelt':'115',
		'rsakv':rsakv,
		'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
		'returntype':'META'
		}
	postData = urllib.urlencode(postData)
	return postData
	
def GetUserName(userName):
	userNameTemp = urllib.quote(userName)
	userNameEncoded = base64.encodestring(userNameTemp)[:-1]
	return userNameEncoded
	
def get_pwd(password, servertime, nonce, pubkey):
	rsaPublickey = int(pubkey, 16)
	key = rsa.PublicKey(rsaPublickey, 65537)
	message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
	passwd = rsa.encrypt(message, key)
	passwd = binascii.b2a_hex(passwd)
	return passwd
	
def sServerData(serverData):
	p = re.compile('\((.*)\)')
	jsonData = p.search(serverData).group(1)
	data = json.loads(jsonData)
	serverTime = str(data['servertime'])
	nonce = data['nonce']
	pubkey = data['pubkey']
	rsakv = data['rsakv']
	#print 'Server time is:', serverTime
	#print 'nonce is:', nonce
	return serverTime, nonce, pubkey, rsakv
	
def sRedirectData(text):
	p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
	loginUrl = p.search(text).group(1)
	#print 'loginUrl is:', loginUrl
	return loginUrl


class WeiboLogin():
	def __init__(self, user, pwd, enableProxy = False):
		print 'Initializing WeiboLogin...'
		self.userName = user
		self.passWord = pwd
		self.enableProxy = enableProxy
		self.serverUrl  = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTgxMDEwODY1ODU%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1472715131141'
		self.loginUrl   =  'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
		self.postHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'}

	def Login(self):
		self.EnableCookie(self.enableProxy)
		serverTime, nonce, pubkey, rsakv = self.GetServerTime()
		postData = PostEncode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)
		
		req = urllib2.Request(self.loginUrl, postData, self.postHeader)
		result = self.opener.open(req)
		text = result.read()
		try:
			loginUrl = sRedirectData(text)
			self.opener.open(loginUrl)
		except:
			print 'Error while redirect'
			return False
		return True
		
	def EnableCookie(self, enableProxy):
		cookiejar = cookielib.LWPCookieJar()
		cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
		
		if enableProxy:
			proxy_support = urllib2.ProxyHandler('http', 'http://xxx.pac')
			self.opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
			print 'Proxy enabled'
		else:
			self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
		
	def GetServerTime(self):
		print 'Getting time and nonce...'
		try:
			serverData = self.opener.open(self.serverUrl).read()
		except:
			traceback.print_exc()
		
		try:	
			serverTime, nonce, pubkey, rsakv = sServerData(serverData)
		except:
			traceback.print_exc()
			print 'Get server time & nonce error!'
			return None
		return serverTime, nonce, pubkey, rsakv
		
		
	
if __name__ == '__main__':
	weiboLogin = WeiboLogin('18101086585', 'test123')
	if weiboLogin.Login() == True:
		print 'Login success'
		data = weiboLogin.opener.open('http://weibo.com/u/5117550866?from=myfollow_all&is_all=1').read()
		f = open('f:\\home.html', 'w+')
		f.write(data)
		f.close()
	else:
		print 'Login failed'