# -*- coding:utf-8 -*-


import SocketServer
from GlobalTools import responseToDown, device_type, cacheObj,sendCommandToDown,config
from threading import Thread
import ast
socket_pool = {}
class Consumer(Thread):
    def run(self):
        global socket_pool
        print "starting Queue Server"
        while True:
            # print socket_pool
            data = cacheObj.brpop('Q', 0)[1]


            if type(data) == type("a"):
                data = ast.literal_eval(data)
            target = data[0]
            command = data[1:len(data)]
            print sendCommandToDown(command,target,device_type, socket_pool,cacheObj)["msg"]
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    # ip = "192.168.1.101"
    # port = 0
    # timeOut = 60

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        # print 1
        # self.request.settimeout(self.timeOut)

    def handle(self):
        global socket_pool
        # global device_type

        while 1:
            try:
                data = self.request.recv(1024).split("\xff")[0] + '\xff'
            except:
                break
                # if data[0] == '\xA5' and data[1] == '\x5A':
                # print ":".join("{:02x}".format(ord(c)) for c in data)

            str = data[2:4]
            device = device_type[str]
            socket_pool[device] = self


            if data[0] == '\xA5' and data[1] == '\x5A':
                pass
                # responseToDown(data, device_type, socket_pool,cacheObj)
                #
                # if cache.get("LIGHT_1_U"):
                #     s = socket_pool["LIGHT_1"]
                #     commandCode = command_code["LIGHT_1"]
                #     makePack(s, commandCode,cache.get("LIGHT_1_U"))
                # if cache.get("DOOR_1_U"):
                #     try:
                #         s = socket_pool["DOOR_1"]
                #         commandCode = command_code["DOOR_1"]
                #         makePack(s, commandCode, cache.get("DOOR_1_U"))
                #     except:
                #         cache.delete("DOOR_1_U")
                #         cache.delete("DOOR_1_D")
                # if cache.get("DESK_1_U"):
                #     try:
                #         s = socket_pool["DESK_1"]
                #         commandCode = command_code["DESK_1"]
                #         makePack(s, commandCode, cache.get("DESK_1_U"))
                #     except:
                #         cache.delete("DESK_1_U")
                #         cache.delete("DESK_1_D")
                # if data[2:4] == "\x00\x01":
                #     dataList = getFloats(data)["content"]
                #     cache.set("LIGHT_1_D", dataList)
                # elif data[2:4] == "\x00\x02":
                #     s = socket_pool["LIGHT_1"]
                #     makePack(s, cache.get("LIGHT_1_U"))
                #     dataList = getFloats(data)["content"]
                #     cache.set("LIGHT_1_D", dataList)
                #     # print """###############
                #     #      get:"""
                #     # print  cache.get("LIGHT_1_D")
                #     # print "###############"
                # elif data[2:4] == "\x00\x03":
                #     s = socket_pool["DESK_1"]
                #     commandCode = command_code["DESK_1"]
                #     makePack(s, commandCode, cache.get("DESK_1_U"))
                #     dataList = getFloats(data)["content"]
                #     print dataList
                #     cache.set("DESK_1_D", dataList)
                # elif data[2:4] == "\x00\x04":
                #     s = socket_pool["DOOR_1"]
                #     commandCode = command_code["DOOR_1"]
                #     makePack(s, commandCode, cache.get("DOOR_1_U"))
                #     dataList = getFloats(data)["content"]
                #     cache.set("DOOR_1_D", dataList)
        socket_pool.pop(device, None)
        print "disconnect to %s" % device


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def StartServer():
    print "starting TCP Server ..."
    s = SocketServer.ThreadingTCPServer(('0.0.0.0', 8007), ThreadedTCPRequestHandler)
    s.serve_forever()



if __name__ == '__main__':
    threadingCount = config["Queue"]["threading_count"]
    for i in range(1):
        c = Consumer()
        c.start()
    StartServer()
