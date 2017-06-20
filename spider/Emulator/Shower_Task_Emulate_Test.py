# -*- coding:utf-8 -*-
# 运行环境：Python 2.7.12

import env
import redis
import json
from spider.Tools.Find_Path import find_json_file

def read_setting_from_json(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		f.close()
		taskListName = setting['taskListName']
		redis_ip = setting['redis_ip']
		redis_port = setting['redis_port']
		return taskListName, redis_ip, redis_port

		
def read_task_from_json(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		f.close()
		return setting
		
if __name__ == '__main__':
	jsonPath = find_json_file('..\\distributor_setting.json')
	taskListName, redis_ip, redis_port = read_setting_from_json(jsonPath)
	taskPath = find_json_file('..\\Shower_Task.json')
	task = read_task_from_json(taskPath)
	r = redis.StrictRedis(redis_ip, redis_port, db = 0)
	try:
		r.ping()
	except:
		print 'Can not connet to redis'
		
	value = json.dumps(task).decode('utf-8')
	try:
		r.lpush(taskListName, value)
	except:
		print 'Failed'
	else:
		print 'success send the task info is', value
	
# http://weibo.com/u/5117550866?from=myfollow_all&is_all=1
# http://iie.ac.cn/
# Y:\\\\Mail_Check\\eml\\locpg
