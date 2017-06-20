# -*- coding:utf-8 -*-
# Python 2.7.12
# Give relative path of the json file, return the absolute path of json file
import sys
import os
import re

# 文件的路径拼接，支持.\和..\方式
def path_join(currentPath, relPath): 
	rg = re.compile(r'([^\.]\.\\)|(^\.\\)')
	relPath = re.subn(rg, '', relPath)[0]
	while relPath[0:3] == '..\\':
		baseName = os.path.basename(currentPath)
		nameLen = len(baseName)
		if nameLen != 0:
			currentPath = currentPath[:-nameLen - 1] 
		relPath = relPath[3:]
	while relPath[0] == '\\':
		relPath = relPath[1:]
	if currentPath[-1] != '\\':
		currentPath += '\\'
	jsonPath = os.path.join(currentPath, relPath)
	return jsonPath
	
# 调用本函数的文件所在的路径为currentPath, relPath是相对于currentPath的相对路径
def find_json_file(relPath):
	currentPath = sys.path[0]
	#print 'currentPath', currentPath
	jsonPath    = path_join(currentPath, relPath)
	return jsonPath
	
def test(relPath):
	path = find_json_file(relPath)
	print path
	
if __name__ == '__main__':
	test('.\\a.txt')
	test('..\\a.txt')
	test('..\\..\\a.txt')
	test('..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\a.txt')
	test('c:\\a.txt')
	test('a')