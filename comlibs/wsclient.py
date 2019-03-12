#!/usr/bin/env python
# encoding: utf-8

from websocket import create_connection
from websocket._abnf import *
from datetime import timedelta

from util.tools import Log

logger = Log().getLog()
PING_TIMEOUT = 3

_ioloop = None
def attach(ioloop):
    global _ioloop
    _ioloop = ioloop

"""
异步websocket客户端：
    1.可集成类tornado的各种ioloop
    2.自动心跳检测

    ws = WSClient()
    ws.create_connection(url)
    ws.send_message(message, do_something_on_receved_data)

"""
class WSClient(object):

    def __init__(self,ioloop = None):
        self.ioloop = ioloop or _ioloop
        self.conn = None
        self.keepalive = None
        self.on_message_callback=None

    def create_connection(self,url):
        self.conn = create_connection(url)
        self.conn.sock.setblocking(0)
        self.ioloop.add_handler(self.conn.fileno(), lambda fd,event:self.recv_message(), self.ioloop.READ)
        self.keepalive = self.ioloop.add_timeout(timedelta(seconds=PING_TIMEOUT), self.heartbeat)

    def close(self):
        self.ioloop.remove_handler(self.conn.fileno())
        self.ioloop.remove_timeout(self.keepalive)
        try:
            self.conn.close()
        except:
            pass

    def heartbeat(self):
        if self.conn.connected:
            self.ping()
            self.keepalive = self.ioloop.add_timeout(timedelta(seconds=PING_TIMEOUT), self.heartbeat)
        else:
            logger.warning('Websocket connection has been closed!')
            self.cose()

    def ping(self,payload=''):
        self.conn.ping(payload)

    def send_message(self,message, callback=None):
        self.on_message_callback=callback
        self.conn.send(message)

    def recv_message(self):
        opcode, data = self.conn.recv_data(True)
        if opcode == ABNF.OPCODE_TEXT:
            if self.on_message_callback:
                try:
                    self.on_message_callback(data)
                except:
                    raise
        elif opcode == ABNF.OPCODE_PONG:
            #忽略pong包
            pass
        else:
            pass
