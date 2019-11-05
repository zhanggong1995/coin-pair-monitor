# coding=utf-8
import os,time,commands
import sys
#币对文件路径
path = "/root/python_program/coin-pair/txt"
#币对个数
number = 7
list_depth = {}
list_trade = {}
if len(sys.argv)!=2:
    print "no argv found"
    exit(-1)
keyword=sys.argv[1]
class Depth:
    def __init__(self,f_path):
        self.path=f_path
        list1=str.split(f_path,"/")
        list2=str.split(list1[-1],".")
        self.exchange=list2[0]
        self.coin=list2[1]
        self.topic=list2[2]
        self.keyword=self.exchange+"."+self.coin
class Trade:
    def __init__(self,f_path):
        self.path=f_path
        list1=str.split(f_path,"/")
        list2=str.split(list1[-1],".")
        self.exchange=list2[0]
        self.coin=list2[1]
        self.topic=list2[2]
        self.keyword = self.exchange + "." + self.coin
status1,depth_path=commands.getstatusoutput('ls '+path+'/*.depth ')
status2,trade_path=commands.getstatusoutput('ls '+path+'/*.trade ')
depth_list=str.split(depth_path)
trade_list=str.split(trade_path)
for i in range(number):
    list_depth[i]=Depth(depth_list[i])
    list_trade[i]=Trade(trade_list[i])
for i in range(number):
    if list_depth[i].keyword==keyword:
        for j in range(number):
            #if list_depth[i].exchange==list_trade[j].exchange and list_depth[i].coin==list_trade[j].coin:
            if list_depth[i].keyword==list_trade[j].keyword:
                time1 = os.stat(list_depth[i].path).st_mtime
                time2 = os.stat(list_trade[j].path).st_mtime
                if time.time() - time1 > 60:
                    print("2 nodata " + list_depth[i].keyword)
                    continue
                elif time.time() - time2 > 60:
                    print("2 nodata " + list_trade[j].keyword)
                    continue
                quote_depth = open(list_depth[i].path, "r")
                quote_trade = open(list_trade[j].path, "r")
                depth = quote_depth.read()
                trade = quote_trade.read()
                quote_depth.close()
                quote_trade.close()

                s1 = depth.split()
                s1.insert(1, trade)
                s2 = [float(k) for k in s1]

                if s2[0]<s2[1] or s2[1]<s2[2]:
                    print("1 " + list_trade[j].keyword + ":" + str(s2))
                else:
                    print("0 " + list_trade[j].keyword + ":" + str(s2))