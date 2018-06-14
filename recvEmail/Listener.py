# -*- coding:utf-8 -*-
# Python2.7.12


import thread

import Controller

class Listener(object):
    def on_error(self, headers, message):
        print('received an error %s' %message)
    def on_message(self, headers, message):
        try:
            print('received a message %s' %message)
        except Exception,e:
            print e
        controller = Controller.Controller(message)
        controller.start()

def recvMsg(conn):
    while conn.is_connected() is False:
        try:
            conn.connect(wait=True)
        except Exception, e:
            pass
    print conn.is_connected()
    conn.subscribe(destination='inspector-forward-queue')
    while True:
        pass

def sendMsg(message):
    print message
    while conn.is_connected() is False:
        try:
            conn.connect(wait=True)
        except Exception, e:
            pass
    print conn.is_connected()
    conn.send(destination='inspector-reply-queue', body=message, content_type='utf-8')

import stomp
conn = stomp.Connection10([('localhost', 61613)])
listener = Listener()
conn.set_listener('', listener)
#conn.start()
#conn.connect(wait=True)
#print conn.is_connected()
while conn.is_connected() is False:
    try:
        conn.connect(wait=True)
    except Exception, e:
        pass
print conn.is_connected()
if __name__ == '__main__':
    thread.start_new_thread(recvMsg(conn), )