# -*- coding:utf-8 -*-
# 作用：方便生成json配置文件
# 运行环境：Python2.7

import json

if __name__ == '__main__':
	dictionary = dict()
	dictionary['localURL']   = 'Z:\\spider_tmp\\data'
	dictionary['list_name']  = 'textqueue'
	dictionary['redis_ip']   = '10.10.17.134'
	dictionary['redis_port'] = 6379
	dictionary['checker_ip'] = '10.10.17.57'
	dictionary['checker_port'] = 5557
	#dictionary['distributor_ip'] = '127.0.0.1'
	#dictionary['distributor_port'] = 10000
	setting = json.dumps(dictionary)
	#fileName = 'receiver_setting.json'
	fileName = 'distributor_setting.json'
	f = open(fileName, 'w+')
	f.write(setting)
	f.close()
	