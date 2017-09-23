# -*- coding:utf-8 -*-
import struct
import redis
import ast
from werkzeug.contrib.cache import MemcachedCache



class Config(object):
    def __init__(self):
        try:
            from config import config
            self.conf = config
        except:
            print u"未找到"

    def getConfig(self, sec):
        return self.conf[sec]

    def getConfigByString(self, str):
        nodeList = str.split(".")
        result = self.conf
        for i in nodeList:
            result = result[i]
        return result


class CacheFactory(object):
    def redisCache(self, url="127.0.0.1", port=6379):
        self.redisPool = redis.ConnectionPool(host=url, port=port)
        self.cache = redis.Redis(connection_pool=self.redisPool)
        return self.cache

    def memcachedCache(self, timeout=0):
        self.cache = MemcachedCache(default_timeout=timeout)
        return self.cache
    def getCache(self):

        cacheType = Config().conf["Cache"]["cache_type"]
        if cacheType == "redis":
            url = Config().conf["Cache"]["redis"]["url"]
            port = Config().conf["Cache"]["redis"]["port"]
            cache = CacheFactory().redisCache(url, port)
        elif cacheType == "memcached":
            timeout = Config().conf["Cache"]["memcached"]["timeout"]
            cache = CacheFactory().memcachedCache(timeout)
        return cache

def responseToDown(data, device_type, socket_pool,cache):

    commandCode = data[2:4]
    if not device_type:
        return
    if commandCode in device_type:
        deviceName = device_type[commandCode]
        s = socket_pool[deviceName]
        upCache = cache.get("%s_U" % deviceName)
        if not upCache:
            upCache = Config().conf["Socket"]["defaultResponse"]
        makePack(s, commandCode, upCache)
        dataList = getFloats(data)["content"]
        cache.set("%s_D" % deviceName, dataList)
def sendCommandToDown(command, target,device_type, socket_pool,cache):
    if not device_type:
        return
    if target in device_type.values():
        if target not in socket_pool:
            return {"status":"failed","msg":"此设备未连接"}
        s = socket_pool[target]
        commandCode =  {value:key for key,value in device_type.iteritems()}[target]
        makePack(s, commandCode, command)
    return {"status": "", "msg": "发送成功"}
def makePack(server, commandNum, dataArray):
    dataStr = ""
    if type(dataArray)==type("a"):

        dataArray = ast.literal_eval(dataArray)

    for i in dataArray:
        dataStr = dataStr + struct.pack('f', float(i))
    print "sending:"
    print dataArray
    server.request.sendall("\xA5\x5A" + commandNum + dataStr + "\xFF")
    print "sended"


def getFloats(data):
    dataCount = (len(data) - 5) / 4
    result = {"status": "ok", "content": []}
    if (len(data) - 5) % 4 != 0:
        result["status"] = "error"
    else:
        for i in range(1, dataCount + 1):
            stat = struct.unpack('f', data[4 * i:4 * i + 4])
            stat = stat.__str__()
            size = len(stat)
            stat = float(stat[1:size - 2])
            stat = round(stat, 2)
            result["content"].append(stat)
    return result


device_type = Config().conf["Socket"]["device_type"]
device_type_need_response = Config().conf["Socket"]["device_type_need_response"]
cacheObj=CacheFactory().getCache()
config = Config().conf
