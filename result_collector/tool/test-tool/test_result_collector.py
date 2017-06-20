# -*- coding:utf-8 -*-
# 用来模拟发送测试数据，测试protobuf等问题

import json
import zmq
import task_pb2
import check_result_pb2
import keyword_list_pb2

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind('tcp://*:5559')
    data = check_result_pb2.CheckResult()
    # 构造task
    task = task_pb2.Task()
    task.hash = 'ABCD1234'
    task.rel_path = 'XinGongSuo/index.htm'
    task_descriptor = {'taskid': 'abc', 'type': 'sitecheck', 'kwds': '秘密', 'task_url': 'www.iie.ac.cn',
                       'task_name': '信息工程研究所', 'dir_name': 'XinGongSuo'}
    task.task_descriptor = json.dumps(task_descriptor)
    target_addition = {'title': '标题', 'parent_id': 'www.iie.ac.cn', 'web_url': 'www.iie.ac.cn',
                       'file_url': 'www.iie.ac.cn', 'rel_path': 'XinGongSuo/index.htm', 'hash': 'ABCD1234'}
    task.target_addition = json.dumps(target_addition)
    data.task.CopyFrom(task)
    keyword = keyword_list_pb2.KeywordItem()
    keyword.kid =1
    keyword.keyword = '绝密'
    hit = data.hit_positions.add()
    # hit = check_result_pb2.HitPosition()
    hit.offset = 11
    hit.context = '这是一个秘密消息'
    hit.encode_hint = check_result_pb2.GBK
    hit.keyword.CopyFrom(keyword)
    data.keyword_serial = 111
    abc = data.SerializeToString()
    print abc
    # socket.send(abc)
    cba = check_result_pb2.CheckResult()
    cba.ParseFromString(abc)
    print cba





if __name__ == '__main__':
    main()

