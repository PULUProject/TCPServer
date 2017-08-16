# -*- coding:utf-8 -*-

import threading
import SocketServer
import struct


from werkzeug.contrib.cache import MemcachedCache

cache = MemcachedCache(default_timeout=0)
socket_pool = {}
device_type = {"\x00\x00": "device_0", "\x00\x01": "LIGHT_1","\x00\x02": "GUN_1", "\x01\x00": "web"
    , "\x02\x00": "H5"}


def makePack(server,dataArray):
    dataStr = ""
    for i in dataArray:
        dataStr =dataStr + struct.pack('f', float(i))
    #print "sending:"
    #print dataArray
    server.request.sendall("\xA5\x5A\x00\x01" + dataStr + "\xFF")
    #print "sended"


def getFloats(data):
    dataCount = (len(data)-5)/4
    result = {"status":"ok","content":[]}
    if (len(data)-5)%4!=0:
        result["status"]="error"
    else:
        for i in range(1,dataCount+1):
            stat = struct.unpack('f', data[4*i:4*i+4])
            stat = stat.__str__()
            size = len(stat)
            stat = float(stat[1:size - 2])
            stat = round(stat, 2)
            result["content"].append(stat)
    return result


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    # ip = "192.168.1.101"
    # port = 0
    # timeOut = 60

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        # self.request.settimeout(self.timeOut)

    def handle(self):
        global socket_pool
        global device_type
        while 1:
            try:
                data = self.request.recv(1024).split("\xff")[0]+'\xff'
            except:
                print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                return
            #if data[0] == '\xA5' and data[1] == '\x5A':
                #print ":".join("{:02x}".format(ord(c)) for c in data)

            str = data[2:4]
            device = device_type[str]
            #print device
            socket_pool[device] = self
            #print socket_pool


            if data[0] == '\xA5' and data[1] == '\x5A':
                if data[2:4] == "\x00\x01":
                    s = socket_pool["LIGHT_1"]

                    makePack(s, cache.get("LIGHT_1_U"))
                    dataList = getFloats(data)["content"]
                    #print "!!!!!!!!!!!"
                    #print ":".join("{:02x}".format(ord(c)) for c in data)
                    cache.set("LIGHT_1_D", dataList)
                    # print """###############
                    #      get:"""
                    #print  cache.get("LIGHT_1_D")
                    #print "###############"
                elif data[2:4] == "\x00\x02":
                    s = socket_pool["LIGHT_1"]

                    makePack(s, cache.get("LIGHT_1_U"))
                    dataList = getFloats(data)["content"]
                    cache.set("LIGHT_1_D", dataList)
                    #print """###############
                    #      get:"""
                    #print  cache.get("LIGHT_1_D")
                    #print "###############"




class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
if __name__ == "__main__":

    s = SocketServer.ThreadingTCPServer(('0.0.0.0', 8007), ThreadedTCPRequestHandler)
    s.serve_forever()     
    print("Server loop running in thread:", server_thread.name)
    print "8007"
