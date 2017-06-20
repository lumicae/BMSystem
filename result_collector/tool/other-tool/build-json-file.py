# -*- coding:utf-8 -*-
# 作用：方便生成json配置文件
# 运行环境：Python2.7

import json

if __name__ == '__main__':
	dictionary = dict()
	dictionary['address_port'] = 'tcp://127.0.0.1:5559'
	dictionary['db_host']  = 'localhost'
	dictionary['db_user']   = 'root'
	dictionary['db_passwd'] = '123456'
	dictionary['db_port'] = 3306
	dictionary['db_db'] = 'securitydb'
	dictionary['db_charset'] = 'utf8'
	settings = json.dumps(dictionary)
	file_name = 'result_collector_config.json'
	f = open(file_name, 'w+')
	f.write(settings)
	f.close()
	