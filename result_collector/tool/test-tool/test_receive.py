# coding=utf-8
import sys
import time
import json
import zmq
import check_result_pb2
import task_pb2

# 接收地址和端端口
addressPort = 'tcp://127.0.0.1:5559'
# 接收地址和端端口
# addressPort = sys.argv[1]


def saveToDB(result, cnt):
    tid = cnt
    # 任务描述信息，将字符串型利用json里的loads转换成字典型
    taskDescriptor = json.loads(result.task.task_descriptor)
    targetAddition = json.loads(result.task.target_addition)
    taskType = taskDescriptor['type']
    if taskType == 'sitecheck':
        hashname = result.task.hash
        task_id = taskDescriptor['taskid']
        page_url = targetAddition['web_url']
        title = targetAddition['title']
        file_url = targetAddition['file_url']
        relative_path = targetAddition['rel_path']
        file_type = ''
        create_time = time.time()
    elif taskType == 'weibocheck':
        pass
    elif taskType == 'emailcheck':
        pass
    print 'Save a task record in table task'
    # 插入数据到result表
    hid = 1
    for i in result.hit_positions:
        resourcefile_id = ''
        keyword_id = ''
        text = i.context.decode('GB2312').encode('UTF-8')
        secure_result = ''
        user_id = ''
        keyword = i.keyword.keyword.encode('UTF-8')
        create_time = time.time()
        print 'Save a result in table result'
        hid += 1


context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind(addressPort)
while True:
    message = socket.recv()
    # 命中信息
    checkInfo = check_result_pb2.CheckResult()
    # 从给出的字符串message中解析出一条信息
    checkInfo.ParseFromString(message)
    print 'check information=', checkInfo
    count = 0
    saveToDB(checkInfo, count)
    count += 1