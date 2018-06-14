# -*- coding:utf-8 -*-
# Python2.7.12
import socket

host = '127.0.0.1'
port = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
flag = s.connect_ex((host, port))
if flag == 0:
    print "Established connection"
    while 1:
        cmd = raw_input("please input cmd:")
        s.sendall(cmd)
else:
    print "Error"
s.close()