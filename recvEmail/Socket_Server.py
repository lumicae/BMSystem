# -*- coding:utf-8 -*-
# Python2.7.12
import commands
import socket

host = '127.0.0.1'
port = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
while 1:
    conn, addr = s.accept()
    print 'Connected by ', addr
    while 1:
        data = conn.recv(1024)
        if len(data.strip()) != 0:
            print data
        else:
            print 'recv error'

conn.close()
