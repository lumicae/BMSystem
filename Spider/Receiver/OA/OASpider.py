# -*- coding:utf-8 -*-
# Python2.7.12
import env
import threading
import traceback
from Queue import Queue
import hashlib
import os
import re
import md5
import sys
import paramiko
from Spider.Tools.Find_Path import find_json_file
import json
import chardet

def read_setting_from_json(jsonURL):
    try:
        f = open(jsonURL, 'r+')
    except:
        print 'Can not find setting file: ',jsonURL
    else:
        setting = json.loads(f.read())
        f.close()
        ftp_ip   = setting['ftp_ip']
        ftp_user = setting['ftp_user']
        ftp_passwd = setting['ftp_passwd']
        ftp_remote_dir = setting['ftp_remote_dir']
        return ftp_ip, ftp_user, ftp_passwd, ftp_remote_dir


class OASpider(threading.Thread):
    Lock       = threading.RLock() #Lock for Total
    Total      = 0
    allThread  = []
    taskQueue  = Queue()
    localURL   = None # 默认配置路径
    
    # 重置
    @staticmethod
    def Reset():
        OASpider.Total      = 0
        OASpider.allThread  = []
        OASpider.taskQueue  = Queue()
        localURL              = None
        
    # 计数加一
    @staticmethod
    def Add_Num():
        OASpider.Lock.acquire()
        OASpider.Total += 1
        OASpider.Lock.release()
        
    # 判断是否所有线程都已没有任务；如果是，返回True
    @staticmethod
    def AllThreadEnd():
        for thread in OASpider.allThread:
            if thread.status == False:
                return False
        return True
        
    def __init__(self, senderQueue):
        threading.Thread.__init__(self)
        self.senderQueue = senderQueue
        self.status      = False
        
    def send_msg(self, task_content):
        self.senderQueue.put(task_content)
    
    def conn(self, ftp_ip, ftp_user, ftp_passwd, ftp_remote_dir):
        print 'ftp_ip is %s, ftp_user is %s, ftp_passwd is %s, ftp_remote_dir is %s' %(ftp_ip, ftp_user, ftp_passwd, ftp_remote_dir)
        sf = paramiko.Transport(ftp_ip, 22)
        sf.connect(username=ftp_user, password=ftp_passwd)
        self.sftp = paramiko.SFTPClient.from_transport(sf)
        self.iterate_dir(OASpider.localURL, ftp_remote_dir)
        sf.close()
    def iterate_dir(self, local, remote):
        try:
            isExists=os.path.exists(local)
            if not isExists:
                os.makedirs(local)
                print 'dir has created'
            else:
                print 'dir exist'
            if os.path.isdir(local):
                self.sftp.chdir(remote)
                for f in self.sftp.listdir(remote):
                    local_dir = os.path.join(local+remote.replace('/', '\\'))
                    if not os.path.exists(local_dir):
                        os.makedirs(local_dir)
                    remote_path = remote + '/' + f
                    local_path = local_dir + '\\' + f
                    
                    try :
                        self.sftp.chdir(remote_path)
                    except:
                        self.sftp.get(remote_path, local_path)
                        file_hash = os.path.splitext(f)[0]
                        task_content = {}
                        task_content['hash'] = file_hash
                        task_content['rel_path'] = local_path
                        self.send_msg(task_content)
                        OASpider.Add_Num()
                    else :
                       self.iterate_dir(local, remote_path)
            else:
                self.sftp.get(remote, local)
        except Exception,e:
            print('download exception:', e)
        
    #def conn(self,ftp_ip, ftp_user, ftp_passwd, ftp_remote_dir):
    #    self.conn = ftplib.FTP(ftp_ip, ftp_user, ftp_passwd)
    #    self.conn.cwd(ftp_remote_dir)        # 远端FTP目录
    #    os.chdir(OASpider.localURL)                # 本地下载目录

    def get_dirs_files(self):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        dir_res = []
        self.conn.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        return (files, dirs)

    def walk(self, next_dir):
        #print 'Walking to', next_dir
        self.conn.cwd(next_dir)
        try:
            os.mkdir(next_dir)
        except OSError,e:
            print 'mkdir exception：', e
        try:
            os.chdir(next_dir)
        except Exception, e:
            print 'chang dir exception:', e
        ftp_curr_dir = self.conn.pwd()
        local_curr_dir = os.getcwd()
        files, dirs = self.get_dirs_files()
        for f in files:
            rel_path = os.path.abspath(f)
            format = os.path.splitext(rel_path)[1]
            fn = OASpider.localURL + '\\' + str(OASpider.Total) + format
            outf = open(fn, 'wb')
            try:
                self.conn.retrbinary('RETR %s' % f, outf.write)
            finally:
                outf.close()
            inf = open(fn, 'rb')
            try:
                file_hash = hashlib.md5(inf.read()).hexdigest()
            finally:
                inf.close()
            #rel_path = '\\' + os.path.relpath(f, OASpider.localURL)

            new_path = os.path.join(os.path.dirname(fn), file_hash) + format
            try :
               os.rename(fn, new_path)
            except Exception,e:
                print 'rename error', e
            print 'download: %s, the hash is %s'%(new_path, file_hash)
            task_content = {}
            task_content['hash'] = file_hash
            task_content['rel_path'] = new_path
            self.send_msg(task_content)
            OASpider.Add_Num()
        for d in dirs:
            os.chdir(local_curr_dir)#切换本地的当前工作目录为d的父文件夹
            self.conn.cwd(ftp_curr_dir)#切换ftp的当前工作目录为d的父文件夹
            self.walk(d) #在这个递归里面，本地和ftp的当前工作目录都会被更改

    def run(self):
        try:
            jsonPath = find_json_file()
            #jsonPath = 'D:\\mediaCheck\\oa_setup\\config.json'
            print 'jsonPath is', jsonPath
            settings = read_setting_from_json(jsonPath)
            self.conn(*settings)
            #self.walk('.')
        except:
            traceback.print_exc()
        self.status = True
