# coding=utf-8
import time
import uuid
import json
import zmq
import MySQLdb
from config.zmq_config import check_result_pb2
import find_json_file

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

def saveToDB(result):
    # 任务描述信息，将字符串型利用json里的loads转换成字典型
    taskDescriptor = json.loads(result.task.task_descriptor)
    targetAddition = json.loads(result.task.target_addition)
    taskType = taskDescriptor['type']
    if taskType == 'sitecheck':
        rid = uuid.uuid1()
        # print 'rid is ',rid
        hashname = result.task.hash
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
        file_type = ''
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
        except Exception, e:
            print 'Error: Task information can not insert into table:',e
    elif taskType == 'weibocheck':
        pass
    elif taskType == 'emailcheck':
        rid = uuid.uuid1()
        hashname = targetAddition['hash']
        task_id = taskDescriptor['taskid']
        mailHeader = json.load(targetAddition['mail_header'])
        page_url = mailHeader['Path'].replace('\\','\\\\')
        title = mailHeader['Subject']
        file_url = ''
        relative_path = targetAddition['rel_path'].replace('\\','\\\\')
        type = ''
        create_time = time.time()
        cur = db.cursor()
        try:
            # 插入数据到task表
            cur.execute("INSERT INTO RESOURCEFILE(id, hashname, task_id, page_url, title, file_url, relative_path, type, create_time)\
                        VALUES('%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%f')"
                        %(rid, hashname, task_id, page_url, title, file_url, relative_path, type, create_time))
            print 'Task id is: ', rid
            print 'Save a task record in table task'
        except Exception, e:
            print 'Error: Task information can not insert into table:',e
    # 插入数据到result表
    for i in result.hit_positions:
        hid = uuid.uuid1()
        resourcefile_id = rid
        keyword_id = ''
        try:
            text = i.context.decode('UTF-8','ignore')
            # print '************************************************************'
            # print text
            # print '************************************************************'
        except Exception,e:
            text = 'Context can not decode'
            print 'Error:Context can not decode:',e
        # text = i.context.decode('GB2312').encode('UTF-8')
        secure_result = ''
        user_id = ''
        keyword = i.keyword.keyword
        create_time = time.time()
        # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", create_time)
        try:
            cur.execute("INSERT INTO CONTEXT(id, resourcefile_id, text, keyword, create_time)\
                        VALUES('%s', '%s', '%s', '%s', '%f')" 
                         %(hid, resourcefile_id, text, keyword, create_time))
            print 'Save a result in table result'
        except Exception, e:
            print 'Error: Context information can not insert into table:',e
        db.commit()
    cur.close()

if __name__ == '__main__':
    # 寻找result_collector_config.json文件
    json_path = find_json_file.findJsonFile('.\\config\\result_collector_config.json')
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
        # print 'check information=', checkInfo
        saveToDB(check_info)
    db.close()








