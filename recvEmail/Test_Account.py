# -*- coding:utf-8 -*-
# Python2.7.12
import imaplib
import json
import logging
import poplib
import socket
import sys

import os

import binascii
from pyDes import des, ECB, PAD_PKCS5


class FileTool():
    def __init__(self):
        pass
    @classmethod
    def read_json_file(cls,path):
        try:
            f = open(path, 'r+')
        except Exception,e :
            logging.error(e)
        else:
            setting = json.loads(f.read())
            f.close()
            username = setting['username']
            password = setting['password']
            type = setting['type']
            if type == 'verfiy':
                protocol = setting['protocol']
                ssl_flag = setting['SSL']
                port = setting['port']
                server_addr = setting['server']
            elif type == 'test_account':
                protocol = 'none'
                ssl_flag = 0
                port = 0
                server_addr = 'none'
            if len(username)<8:
                pad_len = 8 - len(username)
                temp_username = username + '0' * pad_len
            else:
                temp_username = username
            pwd = DESTool.des_descrpt(str(password), str(temp_username[0:8]))
            return str(username), pwd, type, protocol, ssl_flag, port, server_addr

class DESTool:
    def __init__(self):
        pass
    @classmethod
    def des_encrypt(cls, s, key):
        iv = key
        k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(s, padmode=PAD_PKCS5)
        return binascii.b2a_hex(en)

    @classmethod
    def des_descrpt(cls, s, key):
        iv = key
        k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
        return de

host = '127.0.0.1'
port = 50008
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
flag = s.connect_ex((host, port))

def send_msg(message):
    #print message
    logging.info(message)
    try:
        s.sendall(message)
    except Exception,e:
        logging.info(e)

if __name__ == '__main__':
    cur_user_dir = os.path.dirname(sys.path[0])
    root_dir = cur_user_dir + "\\MailDetect"
    log_path = root_dir + "\\log\\" + "test_config.log"
    file = open(log_path, 'w')
    file.close()
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    json_path = root_dir + "\\config\\" + "test_config.json"
    username, password, type, protocol, ssl_flag, port, server_addr = FileTool.read_json_file(json_path)
    if type=='verify':
        if protocol == 'imap':
            if ssl_flag == 0:
                try:
                    server = imaplib.IMAP4(str(server_addr), port)
                except Exception, e:
                    logging.error(e)
                    status = "server_error"
                else:
                    try:
                        server.login(username, password)
                    except Exception,e:
                        logging.error(e)
                        status = "account_error"
                    else:
                        status = "connect"
                        server.logout()
            else :
                try:
                    server = imaplib.IMAP4_SSL(str(server_addr), port)
                except Exception, e:
                    logging.error(e)
                    status = "server_error"
                else:
                    try:
                        server.login(username,password)
                    except Exception,e:
                        logging.error(e)
                        status = "account_error"
                    else:
                        status = "connect"
                        server.logout()
        elif protocol == 'pop3':
            if ssl_flag == 0:
                try:
                    server = poplib.POP3(str(server_addr), port)
                except Exception, e:
                    logging.error(e)
                    status = "server_error"
                else:
                    try:
                        server.user(username)
                        server.pass_(password)
                    except Exception,e:
                        logging.error(e)
                        status = "account_server"
                    else:
                        status = "connect"
                        server.quit()
            else :
                try:
                    server = poplib.POP3_SSL(str(server_addr), port)
                except Exception, e:
                    logging.error(e)
                    status = "server_error"
                else:
                    try:
                        server.user(username)
                        server.pass_(password)
                    except Exception,e:
                        logging.error(e)
                        status = "account_server"
                    else:
                        status = "connect"
                        server.quit()
    elif type=='test_account':
        if "@" not in username:
            protocol = "none"
            server_addr = "none"
            port = 0
            ssl_flag = 0
        else:
            domain = username.split("@")[1]
            if domain == "163.com" or domain == "126.com" or domain == "yeah.net":
                temp_server_addr = "pop3." + domain
                try:
                    server = poplib.POP3_SSL(str(temp_server_addr), 995)
                except Exception, e:
                    logging.error(e)
                    try:
                        server = poplib.POP3(str(temp_server_addr), 110)
                    except Exception, e:
                        logging.error(e)
                        temp_server_addr = "pop." + domain
                        try:
                            server = poplib.POP3_SSL(str(temp_server_addr), 995)
                        except Exception, e:
                            logging.error(e)
                            try:
                                server = poplib.POP3(str(temp_server_addr), 110)
                            except Exception, e:
                                logging.error(e)
                                protocol = "none"
                                server_addr = "none"
                                port = 0
                                ssl_flag = 0
                            else:
                                protocol = "pop"
                                port = 110
                                ssl_flag = 0
                                server_addr = temp_server_addr
                        else:
                            protocol = "pop"
                            port = 995
                            ssl_flag = 1
                            server_addr = temp_server_addr
                    else:
                        protocol = "pop3"
                        port = 110
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "pop3"
                    port = 995
                    ssl_flag = 1
                    server_addr = temp_server_addr
            else:
                temp_server_addr = "imap." + domain
                try:
                    server = imaplib.IMAP4_SSL(str(temp_server_addr),993)
                except Exception,e:
                    logging.error(e)
                    try:
                        server = imaplib.IMAP4(str(temp_server_addr),143)
                    except Exception,e:
                        logging.error(e)
                        temp_server_addr = "mail." + domain
                        try:
                            server = imaplib.IMAP4_SSL(str(temp_server_addr), 993)
                        except Exception, e:
                            logging.error(e)
                            try:
                                server = imaplib.IMAP4(str(temp_server_addr), 143)
                            except Exception, e:
                                logging.error(e)
                                temp_server_addr = "pop3." + domain
                                try:
                                    server = poplib.POP3_SSL(str(temp_server_addr),995)
                                except Exception,e:
                                    logging.error(e)
                                    try:
                                        server = poplib.POP3(str(temp_server_addr), 110)
                                    except Exception,e:
                                        logging.error(e)
                                        temp_server_addr = "pop." + domain
                                        try:
                                            server = poplib.POP3_SSL(str(temp_server_addr), 995)
                                        except Exception,e:
                                            logging.error(e)
                                            try:
                                                server = poplib.POP3(str(temp_server_addr), 110)
                                            except Exception,e:
                                                logging.error(e)
                                                protocol = "none"
                                                server_addr = "none"
                                                port = 0
                                                ssl_flag = 0
                                            else:
                                                protocol = "pop"
                                                port = 110
                                                ssl_flag = 0
                                                server_addr = temp_server_addr
                                        else:
                                            protocol = "pop"
                                            port = 995
                                            ssl_flag = 1
                                            server_addr = temp_server_addr
                                    else:
                                        protocol = "pop3"
                                        port = 110
                                        ssl_flag = 0
                                        server_addr = temp_server_addr
                                else:
                                    protocol = "pop3"
                                    port = 995
                                    ssl_flag = 1
                                    server_addr = temp_server_addr
                            else:
                                protocol = "imap"
                                port = 143
                                ssl_flag = 0
                                server_addr = temp_server_addr
                        else:
                            protocol = "imap"
                            port = 993
                            ssl_flag = 1
                            server_addr = temp_server_addr
                    else:
                        protocol = "imap"
                        port = 143
                        ssl_flag = 0
                        server_addr = temp_server_addr
                else:
                    protocol = "imap"
                    port = 993
                    ssl_flag = 1
                    server_addr = temp_server_addr
        if protocol == "imap":
            try:
                server.login(username, password)
            except Exception,e:
                logging.error(e)
                status = "account_error"
            else:
                status = "connect"
                server.logout()
        elif protocol == "pop3" or protocol == 'pop':
            try:
                server.user(username)
                server.pass_(password)
            except Exception, e:
                logging.error(e)
                status = "account_error"
            else:
                status = "connect"
                server.quit()
        elif protocol == "none":
            status = "error"
        if protocol == "imap" and status == "account_error":
            temp_server_addr = "pop3." + domain
            try:
                server = poplib.POP3_SSL(str(temp_server_addr), 995)
            except Exception,e:
                logging.error(e)
                try:
                    server = poplib.POP3(str(temp_server_addr), 110)
                except Exception,e:
                    logging.error(e)
                    temp_server_addr = "pop." + domain
                    try:
                        server = poplib.POP3_SSL(str(temp_server_addr), 995)
                    except Exception,e:
                        logging.error(e)
                        try:
                            server = poplib.POP3(str(temp_server_addr), 110)
                        except Exception,e:
                            logging.error(e)
                        else:
                            protocol = "pop"
                            port = 110
                            ssl_flag = 0
                            server_addr = temp_server_addr
                    else:
                        protocol = "pop"
                        port = 995
                        ssl_flag = 1
                        server_addr = temp_server_addr
                else:
                    protocol = "pop3"
                    port = 110
                    ssl_flag = 0
                    server_addr = temp_server_addr
            else:
                protocol = "pop3"
                port = 995
                ssl_flag = 1
                server_addr = temp_server_addr
            if protocol == "pop3" or protocol == 'pop':
                try:
                    server.user(username)
                    server.pass_(password)
                except Exception,e:
                    logging.error(e)
                    status = "account_error"
                else:
                    status = "connect"
                    server.quit()
        if protocol == "pop3" and status == "account_error":
            temp_server_addr = "pop." + domain
            try:
                server = poplib.POP3_SSL(str(temp_server_addr), 995)
            except Exception,e:
                logging.error(e)
                try:
                    server = poplib.POP3(str(temp_server_addr), 110)
                except Exception,e:
                    logging.error(e)
                else:
                    protocol = "pop"
                    port = 110
                    ssl_flag = 0
                    server_addr = temp_server_addr
            else:
                protocol = "pop"
                port = 995
                ssl_flag = 1
                server_addr = temp_server_addr
            if protocol == "pop":
                try:
                    server.user(username)
                    server.pass_(password)
                except Exception,e:
                    logging.error(e)
                    status = "account_error"
                else:
                    status = "connect"
                    server.quit()
        if protocol == "pop3" or protocol == "pop":
            protocol = 'pop3'
    data = {"account": username, "status": status, "protocol": protocol, "server":server_addr, "port": port, "ssl":ssl_flag, "type": type}
    json_str = json.dumps(data)
    logging.info(json_str)
    send_msg(json_str)
    s.close()