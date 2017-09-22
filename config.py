# -*- coding:utf-8 -*-

config = \
    {
        "Cache": {
            "cache_type": "redis",
            "redis": {"url": "127.0.0.1", "port": 6379},
            "memchaced": {"timeout": 0}
        },
        "Socket": {
            "device_type":
                {"\x00\x00": "device_0", "\x00\x01": "LIGHT_1", "\x00\x02": "GUN_1", "\x00\x03": "DESK_1",
                 "\x00\x04": "DOOR_1", "\x01\x00": "web", "\x02\x00": "H5"}
        },
        "Queue":{
            "threading_count":4
        }

    }
