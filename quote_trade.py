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

    def hander_trade(resp):
        print("收到信息，处理topic："+ROUTINGKEY[index])
        file_path=""
        price = resp["data"][0]["price"].encode("utf-8")
        topic=resp["topic"].encode("utf-8")
        api=resp["api"].encode("utf-8")


        print (price,api,topic)
        if api != "quote.trade":
            print("api信息不一致")
            return -1
        if ROUTINGKEY[index] == topic:
            #global file_path
            file_path = "txt/" + topic + ".trade"
            print("topic一致，写入"+file_path)
        else:
            #global file_path
            file_path = "txt/" + topic + ".trade"
            print("topic不一致，写入" + file_path)

        file_object = open(file_path, 'w')
        file_object.write(str(price))
        file_object.close()
    while True:
        for index  in range(0,Num):
            print ROUTINGKEY[index]
            resp = client.subscribe('quote.trade', ROUTINGKEY[index], hander_trade)
            print('subscribe result:', json.dumps(resp.result,encoding='utf-8',ensure_ascii=False))
            time.sleep(1)
except Exception as e:
    logging.exception(e)



