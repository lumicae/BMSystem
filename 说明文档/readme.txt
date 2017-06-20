说明：本机已经配置完成，开启redis数据库后便可运行spider.bat文件运行。

[安装]
爬虫模块，没有安装程序，可以将程序文件夹放在任何路径下，本系统中已存放到D:\software\Spider文件夹中

[配置]
D:\software\Spider\distributor_setting.json文件中以key-value形式设置值

key值           value值                        说明
checker_ip      127.0.0.1             检查端ip，这里设置为本地
redis_ip        127.0.0.1             redis数据库ip,这里也设置成本地
checker_port    5557                  检查端开启的端口
redis_port      6379                  redis服务端口
taskListName    task_descriptor       redis中的任务队列名，无需改变
commandListName command_list          redis中的命令队列名，无需改变
localURL        D:\\Web_Check\\Data   数据保存地址

D:\software\Spider\receiver_setting.json文件中以key-value形式设置值

key值             value值                       说明

distributor_port  10003                distributor的task端口号
commander_port    10004                distributor的command端口号 
distributor_ip    127.0.0.1            distributor的ip地址

[运行]
开启只需要点击spider.bat文件
注意：如果程序文件的路径改变，需要修改spider.bat文件