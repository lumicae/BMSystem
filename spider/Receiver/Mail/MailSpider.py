# -*- coding:utf-8 -*-
# Python2.7.12
import threading
import traceback
from Queue import Queue
import email
from email import header
import hashlib
import os
import re
import md5
import sys

def save_file(dir, content):
    try:
        f = open(dir, 'w+')
        f.write(content)
        f.close() 
    except:
        print 'can not create file:', dir
        return False
    else:
        print 'success create a file: ', dir
        return True
        
def open_file(filename):
    try:
        f = open(filename, 'rb')
    except:
        print 'can not read file:', filename
        return None
    else:
        print 'success read a file: ', filename
        return f

        #获得data的md5值
def get_md5(data):
	data = str(data)
	return md5.new(data).hexdigest()   
    
class MailSpider(threading.Thread):
    Lock       = threading.RLock() #Lock for Total
    Total      = 0
    allThread  = []
    taskQueue  = Queue()
    localURL   = None # 默认配置路径
	
    # 重置
    @staticmethod
    def Reset():
        MailSpider.Total      = 0
        MailSpider.allThread  = []
        MailSpider.taskQueue  = Queue()
        localURL              = None
		
    # 计数加一
    @staticmethod
    def Add_Num():
        MailSpider.Lock.acquire()
        MailSpider.Total += 1
        MailSpider.Lock.release()
        
    # 判断是否所有线程都已没有任务；如果是，返回True
    @staticmethod
    def AllThreadEnd():
        for thread in MailSpider.allThread:
            if thread.status == False:
                return False
        return True
        
    def __init__(self, senderQueue):
        threading.Thread.__init__(self)
        self.senderQueue = senderQueue
        self.status      = False
        
        self.mail_relative_path = u''
        self.mail_from = u''
        self.mail_to = u''
        self.mail_subject = u''
        self.mail_data = u''
        self.payload_hash = u''
        self.mail_header_data = {}
        self.relative_path = u''
        self.relative_path_list = []
        self.payload_hash = u''
        self.payload_hash_list = {}

    def add_task(self, url):
        self.taskQueue.put(url)
    
    def get_task(self):
        task = MailSpider.taskQueue.get()
        return task
        
    def send_msg(self, task_content):
        self.senderQueue.put(task_content)
        
     # 解码头部字符串
    def decodeHeaderStr(self, str):
        s = u''
        header_list = []
        try:
            header_list = email.header.decode_header(str)
        # 无法解析Mime文件的头部
        except Exception, e:
            print 'Error === Decode Mime Header Error:', e
            s = u'Information Error'
            return s
        # hl[0]为内容,hl[1]为编码格式
        for hl in header_list:
            # print 'hl[0] =', hl[0]
            # print 'hl[1] =', hl[1]
            # 如果hl[0]有值,就要解析
            if hl[0] != None:
                # print 'hl[0] =', hl[0]
                # 如果hl[1]有值
                if hl[1] != None:
                    # print 'hl[1] =', hl[1]
                    # 解码失败，原因1，h1[1]不是编码
                    try:
                        s += hl[0].decode(hl[1], 'ignore')
                    except Exception, e:
                        print 'Error === Decode String Error: ', e
                        s += u'DecodeError'
                # 如果hl[1]为空
                else:
                    # 解码失败，原因1，hl[0]中含有中文
                    try:
                        s += hl[0]
                    except Exception, e:
                        print 'Error === Decode String Error: ', e
                        s += u'DecodeError'
            return s
        
    # utf-8编码字符串
    def encodeHeaderStr(self, str):
        try:
            str.encode('utf-8', 'ignore')
        except UnicodeDecodeError, e:
            str = 'EncodeError'
            print 'Error === Encode String Error:', e
        finally:
            return str
    
    # 获取邮件信息
    def getMime(self, content):
        mail = email.message_from_file(content)
        return mail
        
    # 获取邮件头部信息
    def fetchHeader(self, mail):
        # print 'Header=================', mail
        self.mail_header_data['Path'] = self.mail_relative_path
        # 从邮件头中找到form,to,subject,data等内容解码并编码为utf-8
        if u'From' in mail:
            self.mail_header_data['X-From'] = self.decodeHeaderStr(mail['From'])
            self.mail_from = self.decodeHeaderStr(mail['From'])
        else:
            self.mail_header_data['X-From'] = u'None'
            self.mail_from = u'None'
        if u'To' in mail:
            self.mail_header_data['X-To'] = self.decodeHeaderStr(mail['To'])
            self.mail_to = self.decodeHeaderStr(mail['To'])
        else:
            self.mail_header_data['X-To'] = u'None'
            self.mail_to = u'None'
        if u'Subject' in mail:
            self.mail_header_data['Subject'] = self.decodeHeaderStr(mail['Subject'])
            self.mail_subject =self.decodeHeaderStr(mail['Subject'])
        else:
            self.mail_header_data['Subject'] = u'None'
            self.mail_subject = u'None'
        if u'Date' in mail:
            self.mail_header_data['Date'] = self.decodeHeaderStr(mail['Date'])
            self.mail_data = self.decodeHeaderStr(mail['Date'])
        else:
            self.mail_header_data['Date'] = u'None'
            self.mail_data = u'None'
        
    # 保存正文和附件
    def saveFile(self, target_file, target_dir, file_payload):
        save_dir_path = os.path.join(MailSpider.localURL, target_dir)
        try:
            os.makedirs(save_dir_path[:-4])
        except Exception, e:
            pass
        # 写入文件的绝对路径
        save_file_path = os.path.join(save_dir_path[:-4], target_file)
        try:
            p_file_2 = open(save_file_path, 'wb')
            # 写入文件的相对路径
            self.relative_path = os.path.join(target_dir[:-4], target_file)
        # 文件名不符合规范异常
        except IOError, e:
            print 'Error === Create File Failure:', e
            self.relative_path = ''
        else:
            if (save_file_path[-3:] == 'txt') or (save_file_path[-4:] == 'html'):
                # 用gb2312解码邮件正文
                # print filePayload.decode('gb2312', 'ignore')
                filePayload = file_payload.decode('gb2312', 'ignore').encode('utf-8')
                p_file_2.write(filePayload)
            if len(self.relative_path) != 0:
                self.relative_path_list.append(self.relative_path)
                p_file_2.close()
    
    # 获取邮件主体，正文和附件并保存成文件
    def fetchBody(self, mail, save_folder_name):
        # print 'Body=====================', mail
        anonymouse_no = 0
        for part in mail.walk():
            if part.is_multipart():
                continue
            file_name = part.get_filename()
            payload = part.get_payload(decode=True)
            if file_name != None:
                file_name = self.decodeHeaderStr(file_name)
                print 'Attachment File=', file_name
            else:
                file_name = unicode(anonymouse_no)
                anonymouse_no += 1
                if part.get_content_subtype() == u'html':
                    file_name += u'.html'
                elif part.get_content_subtype() == u'plain':
                    file_name += u'.txt'
            # self.payloadHash = hashlib.sha256(payload).hexdigest()
            # 保存正文和附件到文件
            self.saveFile(file_name, save_folder_name, payload)
    
    # 获取每个文件的 Hash 值
    def getFileHash(self, path_list):
        for p in path_list:
            path = os.path.join(MailSpider.localURL, p)
            p_file_3 = open(path, 'rb')
            payload_hash = hashlib.md5(p_file_3.read()).hexdigest()
            p_file_3.close()
            self.payload_hash_list[p] = payload_hash
            
    # 检查一封邮件
    def do_one_email(self, emlName, filePointer):
        # 获取邮件信息，把邮件读到内存
        mailMsg = self.getMime(filePointer)
        # 从读到内存的信息中获取邮件头部信息
        self.fetchHeader(mailMsg)
        # 从读到内存的信息中获取邮件主体信息
        self.fetchBody(mailMsg, emlName)
        # 获取每个文件的 Hash 值
        self.getFileHash(self.relative_path_list)
        # 发送hash relativePathList 和 mail_header
        for p in self.relative_path_list:
            task_content = {}
            task_content['hash'] = self.payload_hash_list[p]
            task_content['rel_path'] = p
            task_content['mail_header'] = self.mail_header_data
            print '****************************************'
            print 'payload_hash:', self.payload_hash_list[p]
            print 'rel_path:', p
            print 'mail_header', self.mail_header_data
            print '****************************************'
            self.send_msg(task_content)
        MailSpider.Add_Num()
    
    # 开始任务
    def do_task(self, iterateRoot):
        emlCount = 0
        print 'Default Code ======', sys.getdefaultencoding()
        for root, dirs, files in os.walk(iterateRoot):
            for emlName in files:
                emlCount += 1
                print 'The Num of Eml Files =', emlCount
                if emlName[-4:] == u'.eml':
                    print '\nFind Eml File =', os.path.join(root, emlName)
                    
                    filePath = os.path.join(root, emlName)
                    filePointer = open_file(filePath)
                    self.mail_relative_path = filePath
                if filePointer != None:
                    self.do_one_email(emlName, filePointer)
                    filePointer.close()
                else :
                    continue
        return True
        
    def run(self):
        try:
            task = self.get_task()
            self.do_task(task)
        except:
            traceback.print_exc()
        self.status = True