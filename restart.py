# coding=utf-8
import os,time,commands
import sys,signal
def myHandler(signum, frame):
    (status,process_num)=commands.getstatusoutput("/usr/bin/ps -ef|grep quote_.*.py|grep -v grep|wc -l")
    print ("process_num:"+str(process_num))
    if process_num<2:
        print("启动失败")
        exit(-1)
    else:
        print("启动成功")
        exit(0)
signal.signal(signal.SIGALRM, myHandler)
signal.alarm(3)
(status,output)=commands.getstatusoutput("/root/python_program/coin-pair/start.sh restart")
print status,output
signal.alarm(0)

