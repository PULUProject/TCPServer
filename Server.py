# -*- coding:utf-8 -*-


import SocketServer
import logging
from GlobalTools import responseToDown, device_type, device_type_need_response, cacheObj, sendCommandToDown, config
from threading import Thread
import ast
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s  [%(levelname)s] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
socket_pool = {}


class Consumer(Thread):
    def run(self):
        global socket_pool
        logging.info("starting Queue Server")
        while True:
            # print socket_pool
            try:
                data = cacheObj.brpop('Q', 0)[1]
            except Exception,e:
                logging.error(e)
                continue
            if type(data) == type("a"):
                data = ast.literal_eval(data)
            target = data[0]
            command = data[1:len(data)]
            logging.debug(sendCommandToDown(command, target, device_type, socket_pool, cacheObj)["msg"])


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    ip = ""
    port = 0

    # timeOut = 60

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]

    def handle(self):
        global socket_pool
        device=""
        while 1:
            try:
                data = self.request.recv(1024).split("\xff")[0] + '\xff'
                #超时
            except Exception,e:
                logging.error(e)
                break

                # print ":".join("{:02x}".format(ord(c)) for c in data)

            if data[0] == '\xA5' and data[1] == '\x5A':
                str = data[2:4]
                if str in device_type:
                    device = device_type[str]
                    #根据硬件代码更改
                    socket_pool[device] = self

                else:
                    logging.error("未知设备")
                    return
                if device in device_type_need_response:
                    responseToDown(data, device_type, socket_pool, cacheObj)
        socket_pool.pop(device, None)
        logging.info("disconnect to %s" % device)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def StartServer():
    logging.info("starting TCP Server ...")
    s = SocketServer.ThreadingTCPServer(('0.0.0.0', 8007), ThreadedTCPRequestHandler)
    s.serve_forever()


if __name__ == '__main__':
    threadingCount = config["Queue"]["threading_count"]
    for i in range(1):
        c = Consumer()
        c.start()
    StartServer()
