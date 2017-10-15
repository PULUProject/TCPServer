# -*- coding:utf-8 -*-


import SocketServer
from GlobalTools import responseToDown, device_type, device_type_need_response, cacheObj, sendCommandToDown, config
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
            # print sendCommandToDown(command, target, device_type, socket_pool, cacheObj)["msg"]
            sendCommandToDown(command, target, device_type, socket_pool, cacheObj)

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    ip = ""
    port = 0

    # timeOut = 60

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]

    def handle(self):
        global socket_pool
        # global device_type
        device=""
        while 1:
            try:
                data = self.request.recv(1024).split("\xff")[0] + '\xff'
            except:
                break

                # print ":".join("{:02x}".format(ord(c)) for c in data)

            if data[0] == '\xA5' and data[1] == '\x5A':
                str = data[2:4]

                if str in device_type:
                    device = device_type[str]
                    socket_pool[device] = self
                else:
                    return
                if device in device_type_need_response:
                    responseToDown(data, device_type, socket_pool, cacheObj)
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
    for i in range(4):
        c = Consumer()
        c.start()
    StartServer()
