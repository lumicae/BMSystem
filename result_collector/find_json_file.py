# -*- coding:utf-8 -*-
# Python 2.7.12
# Give relative path of the json file, return the absolute path of json file
import sys
import os
import re

# 文件的路径拼接，支持.\和..\方式
def pathJoin(current_path, rel_path): 
	rg = re.compile(r'([^\.]\.\\)|(^\.\\)')
	rel_path = re.subn(rg, '', rel_path)[0]
	while rel_path[0:3] == '..\\':
		base_name = os.path.basename(current_path)
		name_length = len(base_name)
		if name_length != 0:
			current_path = current_path[:-name_length - 1] 
		rel_path = rel_path[3:]
	while rel_path[0] == '\\':
		rel_path = rel_path[1:]
	if current_path[-1] != '\\':
		current_path += '\\'
	json_path = os.path.join(current_path, rel_path)
	return json_path
	
# 调用本函数的文件所在的路径为currentPath, relPath是相对于currentPath的相对路径
def findJsonFile(rel_path):
	current_path = sys.path[0]
	print 'current_path', sys.path[0]
	json_path = pathJoin(current_path, rel_path)
	print 'rel_path', rel_path
	return json_path
	
def test(rel_path):
	path = findJsonFile(rel_path)
	print path
	
if __name__ == '__main__':
	test('.\\a.txt')
	test('..\\a.txt')
	test('..\\..\\a.txt')
	test('..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\a.txt')
	test('c:\\a.txt')
	test('a')