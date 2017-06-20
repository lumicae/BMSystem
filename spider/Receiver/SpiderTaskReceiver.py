# -*- coding:utf-8 -*-
# 作用: 获取任务，执行爬虫程序
#      	配置检查端的ip、port;
#		配置分发者的ip、port;
# 运行环境: python2.7

import env
import uuid
import zmq
import json
from spider.Zmq_if.DistributorMessage_pb2 import DistributorMessage 
from spider.Receiver.Web.WebSpiderController import *
from spider.Receiver.Weixin.WeixinSpiderController import *
from spider.Receiver.Weibo.WeiboSpiderController import *
from spider.Receiver.Mail.MailSpiderController import *
from spider.Tools.Find_Path import find_json_file
from Queue import Queue
import traceback
import thread

def can_run():
	node = uuid.getnode()
	mac  = uuid.UUID(int = node).hex[-12:]
	if mac == 'f8bc127c658e': 
		return True
	return False

def read_setting_from_json(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		f.close()
		distributor_ip   = setting['distributor_ip']
		distributor_port = setting['distributor_port']
		commander_port = setting['commander_port']
		return distributor_ip, distributor_port, commander_port

class TaskReceiver():
	def __init__(self):
		self.Controllers = {}
		self.TaskNumberList = []
		self.rank = 0x7fffffff
	
	# 从task_descriptor中获得: 保存数据的文件夹名称和网站URL（私有函数）
	def __read_setting_from_task_descriptor(self):
		task = json.loads(self.task_descriptor.decode('utf-8'))
		self.dirName = task['dirname']
		self.startPage = task['siteurl']
		self.taskType = task['type']
		self.taskNum = task['taskid']
		self.rank = int(task['rank'])
		if self.rank == 0: # 经讨论当rank值设为0时，默认为无rank限制的
			self.rank = 0x7fffffff
		self.TaskNumberList.append(self.taskNum)
		
	# 从protobuf结构中获取通信所传递的具体任务信息（私有函数）
	def __read_setting_from_msg(self, msg):
		self.task_descriptor = msg.task_descriptor
		self.__read_setting_from_task_descriptor()
		self.redis_ip = msg.redis_ip
		self.redis_port = msg.redis_port
		self.checker_ip = msg.checker_ip
		self.checker_port = msg.checker_port
		self.localURL = msg.localURL
	
	# 从SpiderTaskDistributer获得任务	
	def get_task(self):
		msg = DistributorMessage()
		msgStr = self.socket.recv()
		print 'Get one task'
		msg.ParseFromString(msgStr)
		self.__read_setting_from_msg(msg)
	
	def get_task_type(self):
		return self.taskType #please make sure it already be set by __read_setting_from_task_descriptor
	
	# 启动网页爬虫
	def start_SpiderController(self, rank = 0x7fffffff):
		controller = SpiderController()
		controller.set_localURL(self.localURL, self.dirName) # 设置本地保存数据的路径
		controller.init_dir() # 创建保留数据的本地目录
		controller.get_task(self.startPage) # 获得任务,即要扫描的网址
		controller.init_spiders(Num_Of_URLSpider = 15, timeout1 = 10, # URLSpider线程数和网络延迟等待时间
								Num_Of_DownloadSpider = 10, timeout2 = 10, # DownloadSpider线程数和网络延迟等待时间
								ip1 = self.checker_ip, port1 = self.checker_port, # Sender配置
								ip2 = self.redis_ip, port2 = self.redis_port, 
								descriptor = self.task_descriptor, rank = rank) 
		self.Controllers['sitecheck'] = controller
		controller.wait_for_end() # 等待全部线程结束
		controller.save_and_exit() # 退出并保存结果
		return True
	
	# 启动微博爬虫
	def start_WeiboSpiderController(self):
		controller = WeiboSpiderController()
		controller.set_localURL(self.localURL, self.dirName)
		controller.get_task(self.startPage)
		controller.init_dir()
		controller.init_spiders(self.checker_ip, self.checker_port,
								self.redis_ip, self.redis_port, self.task_descriptor)
		self.Controllers['weibocheck'] = controller				
		controller.wait_for_end()
		controller.save_and_exit()
	
	# 启动微信爬虫
	def start_WeixinSpiderController(self):
		controller = WeixinSpiderController()
		controller.set_localURL(self.localURL, self.dirName)
		controller.get_task(self.startPage)
		controller.init_dir()
		controller.init_spiders(self.checker_ip, self.checker_port,
								self.redis_ip, self.redis_port, self.task_descriptor)
		self.Controllers['wexincheck'] = controller
		controller.wait_for_end()
		controller.save_and_exit()
	
	def start_MailSpiderController(self):
		controller = MailSpiderController()
		controller.set_localURL(self.localURL, self.dirName)
		controller.get_task(self.startPage)
		controller.init_dir()
		controller.init_spiders(self.checker_ip, self.checker_port, self.redis_ip, self.redis_port,
								self.task_descriptor)
		self.Controllers['mailcheck'] = controller
		controller.wait_for_end()
		controller.save_and_exit()
				
	def listen_and_execute_command(self, commander_ip, commander_port):
		try:
			content = zmq.Context()
			socket = content.socket(zmq.SUB)
			try:
				socket.connect('tcp://' + commander_ip + ':' + str(commander_port))
			except:
				print 'Network error while connecting to commander!\n'
				return
				
			print 'Command Listener Start!\n'
			socket.subscribe('')
			
			while True:
				command = socket.recv()
				command = json.loads(command)
				print 'Get command: ', str(command)
				taskid = command['taskid']
				command_line = command['command']
				tasktype = command['type']
				if taskid in self.TaskNumberList and command_line == 'kill':
					controller = self.Controllers[tasktype]
					controller.kill_children()
				else:
					print 'cannot find the taskid: \"%s\" to kill' %taskid
	
				# end if
			# end while
		except:
			traceback.print_exc()
			
	def run(self, distributor_ip, distributor_port, commander_port):
		try:
			self.context = zmq.Context()
			self.socket = self.context.socket(zmq.PULL)
			self.socket.connect('tcp://' + distributor_ip + ':' + str(distributor_port))
		except:
			print 'Network error while connecting to distributor！'
		print 'Task Receiver Start'
		
		thread.start_new_thread(self.listen_and_execute_command, (distributor_ip, commander_port))
		
		while True:
			try:
				self.get_task() #从SpiderTaskDistributor获得任务，当前任务执行完成后，才会从SpiderTaskDistributor处取任务
				taskType = self.get_task_type()
				print 'Task: ', self.startPage
				if taskType == 'sitecheck':
					self.start_SpiderController(self.rank)
				elif taskType == 'weibocheck':
					self.start_WeiboSpiderController()
				elif taskType == 'weixincheck':
					self.start_WeixinSpiderController()
				elif taskType == 'emailcheck':
					self.start_MailSpiderController()
				else:
					print 'Type error!'
				try:
					self.TaskNumberList.remove(self.taskNum)
				except:
					print 'taskNum:', self.taskNum
					print 'TaskNumberList:', self.TaskNumberList
					print 'Task Num may be doubled.' # 任务号重复时可能出现问题
			except:
				traceback.print_exc()
		
if __name__ == '__main__':
	# if can_run():
		jsonPath = find_json_file('..\\receiver_setting.json')
		settings = read_setting_from_json(jsonPath)
		taskReceiver = TaskReceiver()
		taskReceiver.run(*settings)
		
		
