# -*- encoding:utf-8 -*-
import sys
print sys.getdefaultencoding()
str = 'ÊÇGBK±àÂë'
print repr(str)
print str.decode('gbk')