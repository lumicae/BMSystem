# coding=utf-8
import env
import time
import uuid
import json
import zmq
import MySQLdb
from config import check_result_pb2
from Spider.Tools.Find_Path import find_json_file
import chardet
import sys

# 接收地址和端端口
# addressPort = 'tcp://127.0.0.1:5559'

def readConfigFromJson(json_path):
    try:
        f = open(json_path, 'r+')
    except Exception:
        print 'Can not find config file', json_path
    else:
        settings = json.loads(f.read())
        f.close()
        print settings
        return settings

def saveFileInfo(result):
    # 任务描述信息，将字符串型利用json里的loads转换成字典型
    taskDescriptor = json.loads(result.task.task_descriptor)
    targetAddition = json.loads(result.task.target_addition)
    taskType = taskDescriptor['type']
    if taskType == 'OAcheck':
        rid = uuid.uuid1()
        hashname = targetAddition['hash']
        task_id = taskDescriptor['taskid']
        relative_path = targetAddition['rel_path'].replace('\\','\\\\')
        create_time = time.time()
        page_url = ''
        file_url=''
        title=''
        cur = db.cursor()
        try:
            # 插入数据到task表
            cur.execute("INSERT INTO RESOURCEFILE(id, hashname, task_id, page_url, title, file_url, relative_path, create_time)\
                        VALUES('%s', '%s', '%s', '%s','%s', '%s', '%s', '%f')"
                        %(rid, hashname, task_id, page_url, title, file_url, relative_path, create_time))
            print 'Task id is: ', rid
            print 'Save a task record in table task'
            flag = True
        except Exception, e:
            print 'Error: Task information can not insert into table:',e
            flag = False
        cur.close()
        return flag, rid
    if taskType == 'sitecheck' or taskType == 'weibocheck' or taskType == 'weixincheck':
        rid = uuid.uuid1()
        # print 'rid is ',rid
        hashname = targetAddition['hash']
        # print 'hash is ', hash
        task_id = taskDescriptor['taskid']
        # print 'task_id is ', task_id
        page_url = targetAddition['web_url']
        # print 'page_url is ', page_url
        title = targetAddition['title']
        # print 'title is ', title
        file_url = targetAddition['file_url']
        # print 'file_url is ', file_url
        relative_path = targetAddition['rel_path'].replace('\\','\\\\')
        # print 'path is', relative_path
        create_time = time.time()
        # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", create_time)
        cur = db.cursor()
        try:
            # 插入数据到task表
            cur.execute("INSERT INTO RESOURCEFILE(id, hashname, task_id, page_url, title, file_url, relative_path, create_time)\
                        VALUES('%s', '%s', '%s', '%s','%s', '%s', '%s', '%f')"
                        %(rid, hashname, task_id, page_url, title, file_url, relative_path, create_time))
            print 'Task id is: ', rid
            print 'Save a task record in table task'
            flag = True
        except Exception, e:
            print 'Error: Task information can not insert into table:',e
            flag = False
        cur.close()
        return flag, rid
    elif taskType == 'emailcheck':
        rid = uuid.uuid1()
        hashname = targetAddition['hash']
        task_id = taskDescriptor['taskid']
        mailHeader = targetAddition['mail_header']
        page_url = mailHeader['Path'].replace('\\','\\\\')
        title = mailHeader['Subject']
        file_url = ''
        relative_path = targetAddition['rel_path'].replace('\\','\\\\')
        type = ''
        create_time = time.time()
        cur = db.cursor()
        print 'page_url is', page_url
        print 'title is', title
        try:
            # 插入数据到task表
            cur.execute("INSERT INTO RESOURCEFILE(id, hashname, task_id, page_url, title, file_url, relative_path, type, create_time)\
                        VALUES('%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%f')"
                        %(rid, hashname, task_id, page_url, title, file_url, relative_path, type, create_time))
            print 'Task id is: ', rid
            print 'Save a task record in table task'
            flag = True
        except Exception, e:
            print 'Error: Task information can not insert into table:',e
            flag = False
        cur.close()
        return flag, rid
def saveContext(result, rid):
    # 插入数据到result表
    for i in result.hit_positions:
        hid = uuid.uuid1()
        resourcefile_id = rid
        try:
            #encoding = chardet.detect(i.context)['encoding']
            #if encoding != None:
            #    text = i.context.decode(encoding,'ignore')
            #else:
            #    text = i.keyword.keyword + 'unkown encoding'
            #print 'encode_hint is',i.encode_hint
            dictEncode = {0:'UTF8', 1:'utf-16', 2:'GBK'}
            encoding = dictEncode[i.encode_hint]
            text = i.context.decode(encoding,'ignore')
            #print '************************************************************'
            #print text
            #print '************************************************************'
        except Exception,e:
            text = i.keyword.keyword
            print 'Error:Context can not decode:',e
        # text = i.context.decode('GB2312').encode('UTF-8')
        keyword = i.keyword.keyword
        create_time = time.time()
        cur = db.cursor()
        # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", create_time)
        try:
            cur.execute("INSERT INTO CONTEXT(id, resourcefile_id, text, keyword, create_time)\
                        VALUES('%s', '%s', '%s', '%s', '%f')" 
                         %(hid, resourcefile_id, transferContent(text), keyword, create_time))
            print 'Save a context in table result'
        except Exception, e:
            print 'Error: Context information can not insert into table:',e
        cur.close()

#如果不加以下处理，不能保存
def transferContent(content):
    if content is None:
        return None
    else:
        string = ""
        for c in content:
            if c == '"':
                string += '\\\"'
            elif c == "'":
                string += "\\\'"
            elif c == "\\":
                string += "\\\\"
            else:
                string += c
        return string
def saveToDB(result):
    flag, rid = saveFileInfo(result)
    if flag:
        saveContext(result, rid)
    else:
         print "save FileInfo except, the context not saved"
    db.commit()
 
if __name__ == '__main__':
    # 寻找result_collector_config.json文件
    json_path = find_json_file()
    #json_path = 'D:\\mediaCheck\\oa_setup\\config.json'
    settings = readConfigFromJson(json_path)
    address_port = settings['address_port']
    db_host = settings['db_host']
    db_user = settings['db_user']
    db_passwd = settings['db_passwd']
    db_port = settings['db_port']
    db_db = settings['db_db']
    db_charset = settings['db_charset']
    
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(address_port)
    try:
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd,
                            port=db_port, db=db_db,charset=db_charset)
        print 'MySQL Connect Success'
    except Exception:
        print 'MySQL Connect Error'
    while True:
        message = socket.recv()
        # 命中信息
        check_info = check_result_pb2.CheckResult()
        # 从给出的字符串message中解析出一条信息
        check_info.ParseFromString(message)
        #print 'check information=', check_info
        saveToDB(check_info)
    db.close()