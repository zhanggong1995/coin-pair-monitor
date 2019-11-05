# -*- coding: utf-8 -*-
# @Author: zhangcb
# @Date:   2018-08-30 15:44:05
# @Last Modified by:   zhangcb
# @Last Modified time: 2019-05-24 12:51:54

import struct,threading,socket,random,uuid,json,time,zlib,hashlib,traceback
from Queue import Queue
from heapq import heappush,heappop
from collections import OrderedDict
from threading import Thread, Lock

MSGID = 0

def crc16(x):
    crc16_table = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5,
            0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad,
            0xe1ce, 0xf1ef, 0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294,
            0x72f7, 0x62d6, 0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c,
            0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7,
            0x44a4, 0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf,
            0xc5ac, 0xd58d, 0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6,
            0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe,
            0xd79d, 0xc7bc, 0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861,
            0x2802, 0x3823, 0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969,
            0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50,
            0x3a33, 0x2a12, 0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58,
            0xbb3b, 0xab1a, 0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03,
            0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b,
            0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32,
            0x1e51, 0x0e70, 0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a,
            0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d,
            0xf14e, 0xe16f, 0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025,
            0x7046, 0x6067, 0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c,
            0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214,
            0x6277, 0x7256, 0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f,
            0xd52c, 0xc50d, 0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447,
            0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e,
            0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676,
            0x4615, 0x5634, 0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9,
            0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1,
            0x3882, 0x28a3, 0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8,
            0xabbb, 0xbb9a, 0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0,
            0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b,
            0x9de8, 0x8dc9, 0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83,
            0x1ce0, 0x0cc1, 0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba,
            0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2,
            0x0ed1, 0x1ef0]
    crc = 0x0000
    for byte in x:
        da = 0xff & (crc/256)
        crc = 0xffff & (crc<<8)
        num = da ^ ord(byte)
        if num < 0:
            num += 256
        crc ^= crc16_table[num]
    return crc;

def crc16_encode(x, crcValue):
    i = 0
    crcValue = crcValue&0xff;
    ret = b''
    for byte in x:
        byte = ord(byte)^crcValue
        ret += chr(byte)
    return ret


    
class MsgRequest:
    Compress = False

    def __init__(self,api):
        self.messageId = 0
        self.requestType = 1
        self.api = api
        # Python 支持 json
        self.serializeType = 2
        self.compress = MsgRequest.Compress
        self.params = {}
    def initMessageId(self):
        global MSGID
        mutex.acquire() 
        MSGID += 1
        self.messageId = MSGID
        mutex.release()
        return self.messageId
    def addParam(self, key, value):
        self.params[key] = value

    def getParam(self, key):
        return self.params[key]

    def removeParam(self, key):
        del self.params[key]

    def addParams(self, params):
        for k in params:
            self.addParam(k, params[k])

    def getSortedParams(self):
        keys=self.params.keys()
        heap=[]
        for item in keys:
            heappush(heap,item)

        sort=[]
        while heap:
            sort.append(heappop(heap))

        resMap=OrderedDict()
        for key in sort:
            resMap[key]=self.params[key]
        return resMap
    def makeSign(self, key):
        ret = key
        keys=self.params.keys()
        heap=[]
        for item in keys:
            heappush(heap,item)

        sort=[]
        while heap:
            sort.append(heappop(heap))

        resMap=OrderedDict()
        for key in sort:
            ret += str(self.params[key])
        md5value = hashlib.md5(ret).hexdigest()
        return md5value

    def pack(self, key):
        tag = self.serializeType
        tag = tag<<1
        tag = tag ^ self.compress
        
        data = {
        "api": self.api,
        "messageId": self.messageId,
        "requestType": self.requestType,
        "serializeType":self.serializeType,
        "compress":self.compress,
        "params":self.getSortedParams(),
        "sign":self.makeSign(key)
        }

        if self.serializeType == 2:
            data = json.dumps(data).encode('utf-8')
        if self.compress:
            data = zlib.compress(data,-1)
        crcValue = crc16(data)
        buf = struct.pack('!BH',tag, crcValue)
        data = crc16_encode(data, crcValue)
        buf += data
        return buf
        
class MsgResponse:

    def __init__(self):
        self.result = None

    def unpack(self, bytes):
        arr = struct.unpack('!BH',bytes[0:3])
        tag = arr[0]
        crcValue = arr[1]
        data = bytes[3:]
        data = crc16_encode(data, crcValue)

        recvCrcValue = crc16(data)
        if crcValue != recvCrcValue:
            print("CRC错误")
        else:
            self.compress = ((tag&1)==1)
            self.serializeType = (tag>>1);
            if self.compress:
                data = zlib.decompress(data)
            if self.serializeType == 2:
                data = json.loads(data)
            self.messageId = data['messageId']
            self.requestType = data['requestType']
            if data.has_key('errCode'):
                self.result = {'errCode':data["errCode"],'errInfo':data["errInfo"]}
            else:
                self.result = data['result']

# status 0 init ApiClient
# status 1 first connect 
#        2 first connected
#        3 first initToken
#        4 reconnecting
#        5 reconnected
#        6 re InitToken
class ApiClient:
    def __init__(self,co_no,opor_no,key):
        self.co_no = co_no
        self.opor_no = opor_no
        self.key = key
        self.token = ""
        self.id = int(random.uniform(1000, 9999))
        self.mac = self.getLocalMac()
        self.rpcMap = {}
        self.subscribeMap = {}
        self.connection = None
        self.timeout = 60
        self.status = 0 
        self.reconn = threading.Event()
        self.t = MessageHandler(self, self.rpcMap, self.subscribeMap)
        self.t.setDaemon(True)
        self.t.start()
        self.pong = time.time()
        self.heartbeatInterval = 15
        self.isFirstConn = False
        self.statusMutex = threading.Lock()

        self.rt = ReconnectThread(self)
        self.rt.setDaemon(True)
        self.rt.start()

        self.ht = HeartbeatThread(self)
        self.ht.setDaemon(True)
        self.ht.start()

    def getLocalMac(self):
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e+2] for e in range(0,11,2)])
    def initToken(self):
        req = MsgRequest("token")
        req.addParam("m", self.mac)
        req.addParam("i",self.id)
        req.addParam("c", self.co_no)
        req.addParam("o", self.opor_no)
        try:
            self.checkSend(req)
            data = req.pack(self.key)
            lenbuf = struct.pack('!i',len(data))
            rpcLock = Queue(1)
            self.rpcMap[req.messageId] = rpcLock;

            print(self.id,'Send init token request')
            self.connection.sendall(lenbuf+data)
            # 等待 5 秒
            resp = rpcLock.get(True, 3)
        except:
            self.rpcMap[req.messageId] = None
            if self.connection == None and self.status == 2:
                print('Connection is intercepted')
                self.status = 0
                self.connect(self.host, self.port)
                time.sleep(1)
                return self.initToken()
            else:
                return False
        if 'token' in resp.result:
            self.token = resp.result['token']
            print("#   Token:"+self.token)
            print("# ----------- Now Can Send Message ----------")
            self.status = self.status + 1;
            return True
        else:
            print("Error:",resp.result)
            return False

    def checkSend(self, req):
        if req.messageId == 0:
            req.initMessageId()
        # 数字签名
        req.makeSign(self.key)
        # 设置Token
        req.token = self.token

    def connect(self, host, port):
        self.host = host
        self.port = port
        if self.status == 0:
            self.status = 1 # first connecting
        else:
            self.status = 4 # reconnecting
        while self.status !=  2 and self.status != 5:
            try:
                # 连接
                connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                connection.settimeout(15)
                connret = connection.connect((host, port))
                self.connection = connection
                print("#   Connect Success!", connection, connret)
                self.status = self.status + 1; 
                return True
            except:
                print("#   Connect Error, Retry 1 second later!")
                self.connection = None
                time.sleep(1)
            
        return False

    def reconnect(self):
        print('reconnect...')
        
        self.status = 4;
        
        while self.status != 6:
            if self.connect(self.host,self.port):
                if self.initToken() == False:                
                    print('initToken Failed, retry 3 second later!')
                    time.sleep(3)

        # 如果有订阅就重新订阅， 如果在重新订阅的过程断开，就走心跳机制
        for key in self.subscribeMap:
            arr = key.split('#')
            handler = self.subscribeMap[key]
            api = arr[0]
            topic = arr[1]
            req = MsgRequest(api)
            req.requestType = 3
            req.addParam("api", api)
            req.addParam("topic", topic)
            resp = self.request(req,handler)
            print('re subscribe '+api+','+topic)
            req = MsgRequest(api)
            req.requestType = 2
            req.addParam("api", api)
            req.addParam("topic", topic)
            self.request(req,handler)
        return True

    def request(self, req, handler=None):
        self.checkSend(req)
        data = req.pack(self.key)
        lenbuf = struct.pack('!i',len(data))
        rpcLock = Queue(1)
        self.rpcMap[req.messageId] = rpcLock;
        print('send request')
        self.connection.sendall(lenbuf+data)
        # 等待 5 秒
        try:
            return rpcLock.get(True, self.timeout)
        except:
            return None

    def getApi(self, api, params):
        if self.token == "":
            print('no Token Check initToken')
        else:
            req = MsgRequest(api)
            req.addParams(params)
            resp = self.request(req)
            if resp == None:
                return None
            return resp.result
    def subscribe(self, api, topic, handler):
        if self.token == "":
            print('no Token Check initToken')
        else:
            req = MsgRequest(api)
            req.requestType = 2
            req.addParam("api", api)
            req.addParam("topic", topic)
            self.subscribeMap[api+"#"+topic] = handler
            return self.request(req,handler)
    def unsubscribe(self, api, topic, handler):
        if api+"#"+topic not in self.subscribeMap:
            return None
        else:
            req = MsgRequest(api)
            req.requestType = 3
            req.addParam("api", api)
            req.addParam("topic", topic)
            del self.subscribeMap[api+"#"+topic];
            return self.request(req,handler)
    def ping(self):
        req = MsgRequest("ping")
        req.requestType = 0
        if req.messageId == 0:
            req.initMessageId()
        req.addParam("api", "ping")
        req.addParam("d", int(round(time.time() * 1000)))
        data = req.pack(self.key)
        lenbuf = struct.pack('!i',len(data))
        print('send ping')
        self.connection.sendall(lenbuf+data)
    def stop(self):
        print('close ApiClient')
        self.connection.close()
        self.t.stop()


class HeartbeatThread(Thread):
    def __init__(self, client):
        Thread.__init__(self)
        self.client = client
    def run(self):
        while True:
            # 重新连接的过程心跳关闭
            if self.client.reconn.isSet() or self.client.connection == None or self.client.token == None:
                time.sleep(5)
                continue;
            self.lastping = time.time()
            try:
                self.client.ping()
                time.sleep(self.client.heartbeatInterval)
            except:
                traceback.print_exc()
                print('Heartbeat pack send failed')
                self.client.pong = self.lastping - self.client.heartbeatInterval*2
            #如果心跳
            if self.lastping - self.client.pong >= self.client.heartbeatInterval*2:
                print('Heartbeat force to reconnect')
                if self.client.connection != None:
                    self.client.connection.close()
                    self.client.connection = None
                if self.client.reconn.isSet() == False:
                    self.client.reconn.set()


class ReconnectThread(Thread):
    def __init__(self, client):
        Thread.__init__(self)
        self.client = client
        self.client.reconn = threading.Event()
    def run(self):
        while True:
            if self.client.connection == None:
                if self.client.reconn.isSet():
                    try:
                        self.client.reconnect();
                    except:
                        # 重新连接发生异常后就重新reconnect
                        self.client.connection = None;
                        #traceback.print_exc()
                        print('Reconnect Error')
                        continue;
                    self.client.reconn.clear()
                time.sleep(3)
                continue
            else:
                time.sleep(1)
                continue


class MessageHandler(Thread):
    def __init__(self, client, rpcMap, subscribeMap):
        Thread.__init__(self)
        self.client = client
        self.rpcMap = rpcMap
        self.subscribeMap = subscribeMap
    def run(self):
        bytes = b'';
        while True:
            if self.client.connection == None:
                time.sleep(0.01)
                continue;
            #数据包的长度
            try:
                bufBytes = self.client.connection.recv(4-len(bytes))
                bytes += bufBytes
                if len(bytes) == 0:
                    self.client.connection = None
                    self.client.reconn.set()
                    continue
                elif len(bytes)<4:
                    continue
            except:
                bytes = b''
                time.sleep(0.01)
                continue

            packLen = struct.unpack('!i',bytes)[0]
            bytes = b''

            recvSize = 0
            recvData = b'' # 空byte数组
            while recvSize < packLen:
                try:
                    if packLen-recvSize>4096:
                        data = self.client.connection.recv(4096)
                    else:
                        data = self.client.connection.recv(packLen-recvSize)
                    # 如果消息传输过程中，连接断开
                    if len(data) == 0:
                        self.client.connection = None
                        self.client.reconn.set()
                        break;
                    recvSize += len(data)
                    recvData += data
                except:
                    self.client.connection = None
                    self.client.reconn.set()
                    break
            if self.client.connection == None:
                continue
            # 获得完整的包，进行解压成MsgResponse
            resp = MsgResponse()
            resp.unpack(recvData)
            # 转发，或者丢弃
            # RPC 的返回
            if resp.messageId > 0 and resp.messageId in self.rpcMap:
                rpcLock = self.rpcMap[resp.messageId]
                del self.rpcMap[resp.messageId]
                rpcLock.put(resp, True)
            # 如果是个订阅返回
            elif resp.requestType == 2:
                if resp.result:
                    topic = resp.result['topic']
                    api = resp.result['api']
                    if api+"#"+topic in self.subscribeMap:
                        call = self.subscribeMap[api+"#"+topic]
                        call(resp.result)
                    else:
                        print('not a subscribe msg')
                else:
                    print('no result message')
            elif resp.requestType == 0:
                self.client.pong = time.time()
                continue;
            else:
                print('other type resp：')
                print(resp.messageId,resp.requestType, resp.result)

mutex = Lock()