# -*- coding:utf-8 -*-
# 运行环境：Python 2.7.12

import env
import redis
import json
from Spider.Tools.Find_Path import find_json_file

def read_setting_from_json(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		f.close()
		commandListName = setting['commandListName']
		redis_ip = setting['redis_ip']
		redis_port = setting['redis_port']
		return commandListName, redis_ip, redis_port

		
def read_command_from_json(jsonURL):
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
	commandListName, redis_ip, redis_port = read_setting_from_json(jsonPath)
	commandPath = find_json_file('..\\Shower_Command.json')
	command = read_command_from_json(commandPath)
	r = redis.StrictRedis(redis_ip, redis_port, db = 0)
	print redis_ip
	try:
		r.ping()
	except:
		print 'Can not connet to redis'

	value = json.dumps(command).decode('utf-8')
	try:
		r.lpush(commandListName, value)
	except:
		print 'Failed'
	else:
		print value
		print 'Success'
	