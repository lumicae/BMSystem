# -*- coding:utf-8 -*-
# 作用: 具体的爬虫实现
# 运行环境: Python2.7

import env
import threading
import traceback
import zmq
import sys
import redis
import json
from spider.Zmq_if import Task_pb2
from spider.Receiver.Web.WebSpider import *
from spider.Receiver.Weibo.WeiboSpider import *
from spider.Receiver.Weixin.WeixinSpider import *
from spider.Receiver.Mail.MailSpider import *
from Queue import Queue

reload(sys)
sys.setdefaultencoding('utf-8')

#与检查端实时交互	
class Sender(threading.Thread):
	queue = Queue() #任务队列
	num   = 0 #发送的消息数
	Lock  = threading.RLock() #Lock for num
	allThread = [] #所有的Sender线程
	localURL = ''
	
	#重置
	@staticmethod
	def Reset():
		Sender.queue     = Queue() #任务队列
		Sender.num       = 0 #发送的消息数
		Sender.allThread = [] #所有的Sender线程
		Sender.localURL  = ''
	
	#发送的消息数增加一
	@staticmethod
	def Add_Num():
		Sender.Lock.acquire()
		Sender.num += 1
		Sender.Lock.release()		
	
	def __init__(self, checker_ip, checker_port, redis_ip, redis_port, task_descriptor):
		threading.Thread.__init__(self)
		self.kill            = False
		self.checker_ip      = checker_ip
		self.checker_port    = checker_port
		self.task_descriptor = task_descriptor
		self.connect_to_redis(redis_ip, redis_port) #连接redis数据库
		self.get_task_id() #获得任务名
		self.connect_to_redis(redis_ip, redis_port)
		self.redisStatus = self.ping()
		
	#连接redis数据库
	def connect_to_redis(self, ip , port):
		self.redis = redis.StrictRedis(ip, port, db = 0)
		return self.redis
	
	#判断是否能ping通
	def ping(self):
		try:
			self.redis.ping()
		except:
			return False
		return True
	
	#获取task名称，即网站id
	def get_task_id(self):
		descriptor = json.loads(self.task_descriptor.decode('utf-8'))
		self.taskId = 'Spider_' + descriptor['taskid'] #以网站名拼音命名文件夹和任务名
	
	#向检查方发送消息
	def send_msg_to_checker(self, msg, socket, task_content):
		msg.task_descriptor      = self.task_descriptor
		task_content['rel_path'] = task_content['rel_path'][len(Sender.localURL):]
		msg.rel_path             = task_content['rel_path']
		msg.hash                 = task_content['hash']
		task_content             = json.dumps(task_content)
		msg.target_addition      = task_content
		
		msgStr = msg.SerializeToString()
		#print msgStr
		socket.send(msgStr) #发送消息
		Sender.Add_Num()
	
	def can_exit(self):
		if not URLSpider.AllThreadEnd():
			return False
		if not DownloadSpider.AllThreadEnd(): 
			return False
		if not WeiboSpider.AllThreadEnd():
			return False
		if not WeixinSpider.AllThreadEnd():
			return False
		if not MailSpider.AllThreadEnd():
			return False
		return True
		
	def run(self):
		try:
			msg     = Task_pb2.Task()
			context = zmq.Context()
			socket  = context.socket(zmq.PUSH)
			socket.connect('tcp://' + self.checker_ip + ':' + str(self.checker_port))
			while True:
				if self.kill:
					break
				try:
					task_content = Sender.queue.get(True, 1)
				except:
					if self.can_exit():
						break
				else:
					#向检查方发送消息
					self.send_msg_to_checker(msg, socket, task_content) 
					#将当前运行情况写入redis
					if self.redisStatus and Sender.num%50 == 0:
						try:
							self.redis.set(self.taskId, False) #将任务未完成状态写入redis
							self.redis.set(self.taskId + '_Num', Sender.num) #将任务完成量写入redis
						except:
							print 'please check the connection with redis!'
					# end if
				# end if
			# end while
			socket.close()
			# print 'Sender exit'
			# print 'Sender is running:' + 'tcp://' + self.checker_ip + ':' + str(self.checker_port)
			if self.redisStatus:
				try:
					self.redis.set(self.taskId, True) #将任务完成状态写入redis
					self.redis.set(self.taskId + '_Num', Sender.num)
				except:
					print 'please check the connection with redis!'
		except:
			traceback.print_exc()
