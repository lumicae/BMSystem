import env
import zmq
import json
from Spider.Zmq_if import Task_pb2
from Spider.Tools.Find_Path import find_json_file

def show(dict):
	try:
		for key in dict:
			print key + ': ' + dict[key]
	except:
		print dict
		exit(0)

def read_setting_from_json(jsonURL):
	try:
		f = open(jsonURL, 'r+')
	except:
		print 'Can not find setting file: ',jsonURL
	else:
		setting = json.loads(f.read())
		f.close()
		checker_ip = '127.0.0.1'
		checker_port = setting['checker_port']
		return checker_ip, checker_port
		
def main():
	jsonPath = find_json_file('..\\distributor_setting.json')
	checker_ip, checker_port = read_setting_from_json(jsonPath)
	context = zmq.Context()
	socket = context.socket(zmq.PULL)
	ip = checker_ip
	port = str(checker_port)
	socket.bind('tcp://' + ip + ':' + port)
	print 'tcp://' + ip + ':' + port
	while True:
		task = Task_pb2.Task()
		msg = socket.recv()
		print '-----------------------------'
		print msg
		'''
		task.ParseFromString(msg)
		dict1 = json.loads(task.task_descriptor)
		dict2 = json.loads(task.target_addition)
		print 'hash:', task.hash
		print 'rel_path', task.rel_path
		show(dict2)
		show(dict1)
		'''
		print '-----------------------------'
		
if __name__ == '__main__':
	main()

