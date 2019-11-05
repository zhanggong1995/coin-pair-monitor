# -*- coding: utf-8 -*-
import ApiClient,json,time,sys
import logging
import re

HOST=sys.argv[1]
ROUTINGKEY=re.split('[,]',sys.argv[2])
Num=len(ROUTINGKEY)
print Num
print ROUTINGKEY[0]
client = ApiClient.ApiClient(2160,216000001,'YTVmMzk4NzdiZDIzOTYyZTcyMzlkNzM5NDA0NmMwNzI=')
client.connect(HOST,6767)
print("connect to ",HOST)

client.timeout = 15

try:
    st = time.time()
    client.initToken()

    def hander_depth(resp):
        print("收到信息，处理topic："+ROUTINGKEY[index])
        file_path=""
        data_ask=resp["asks"][4]["price"]
        data_bids=resp["bids"][4]["price"]
        topic=resp["topic"].encode("utf-8")
        api=resp["api"].encode("utf-8")

        print (data_ask,data_bids,api,topic)
        if api != "quote.depth":
            print("api信息不一致")
            return -1
        if ROUTINGKEY[index] == topic:
            #global file_path
            file_path = "txt/" + topic + ".depth"
            print("topic一致，写入"+file_path)
        else:
            #global file_path
            file_path = "txt/" + topic + ".depth"
            print("topic不一致，写入" + file_path)

        file_object = open(file_path, 'w')
        file_object.write(str(data_ask)+" "+str(data_bids))
        file_object.close()
    while True:
        for index  in range(0,Num):
            print ("订阅："+ROUTINGKEY[index])
            resp = client.subscribe('quote.depth', ROUTINGKEY[index], hander_depth)
            print('subscribe result:', json.dumps(resp.result,encoding='utf-8',ensure_ascii=False))
            time.sleep(1)
except Exception as e:
    logging.exception(e)




