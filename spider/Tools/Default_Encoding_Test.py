# -*- encoding:utf-8 -*-
import sys
print sys.getdefaultencoding()
str = '��GBK����'
print repr(str)
print str.decode('gbk')