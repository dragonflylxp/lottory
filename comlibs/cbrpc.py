#encoding=utf-8

import msgpackrpc
import traceback
import threading
import Queue
import time
from contextlib import contextmanager
from tornado import ioloop
from util.configer import *

from util.tools import Log
logger = Log().getLog()

class Loop(object):
    """\
    An I/O loop class which wraps the Tornado's ioloop.
    """

    @staticmethod
    def instance():
        return Loop(ioloop.IOLoop.current())

    def __init__(self, loop=None):
        self._ioloop = loop or ioloop.IOLoop()
        self._ioloop.make_current()
        self._periodic_callback = None

    def start(self):
        if not self._ioloop._running:
            self._ioloop.start()
        else:
            time.sleep(0.1)

    def stop(self):
        try:
            self._ioloop.stop()
        except:
            return

    def attach_periodic_callback(self, callback, callback_time):
        if self._periodic_callback is not None:
            self.dettach_periodic_callback()

        self._periodic_callback = ioloop.PeriodicCallback(callback, callback_time, self._ioloop)
        self._periodic_callback.start()

    def dettach_periodic_callback(self):
        if self._periodic_callback is not None:
            self._periodic_callback.stop()
        self._periodic_callback = None


class CBClient(msgpackrpc.Client):

    def __init__(self, host, port, loop=None):
        try:
            self.origin_ioloop = loop
            super(CBClient, self).__init__(msgpackrpc.Address(host, port),timeout=10)#,loop=Loop(loop))
        except Exception as e:
            raise


    def call(self, method, *args):
        """
        @params: method   调用方法
        @params: args     参数列表
        """

        try:
            #转成unicode，兼容python3.x
            for arg in args:
                if isinstance(arg, dict):
                    for k,v in arg.iteritems():
                        if isinstance(v,str):
                            arg[k.decode('utf-8')] = v.decode('utf-8')
                elif isinstance(arg, list):
                    arg = [v.decode('utf-8') if isinstance(v, str) else v for v in arg]
                else:
                    arg = arg.decode('utf-8') if isinstance(arg, str) else arg
            return super(CBClient, self).call(method, *args)
        except Exception as e:
            raise
        finally:
            #将调用方的ioloop重置为current
            if self.origin_ioloop:
                self.origin_ioloop.make_current()

class CBServer(msgpackrpc.Server):

    def __init__(self, rpcobj, port, ips="127.0.0.1"):
        super(CBServer, self).__init__(rpcobj)
        self.listen(msgpackrpc.Address(ips, port))

    def current_ioloop(self):
        return self._loop._ioloop


RpcException = msgpackrpc.error.RPCError

class RpcConnectionPool():

    def __init__(self, host='127.0.0.1', port=7000, max_connections=10, rpc_name="", ioloop=None):
        self.max_connections = max_connections
        self.cur_connections = 0
        self.pools = Queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.ioloop = ioloop
        self.name = rpc_name

    def get_conn(self):
        with self.lock:
            if self.cur_connections >= self.max_connections:
                raise MaxConnections("Too many connections! name={}|max={}|cur={}|qsize={}".format( \
                        self.name,self.max_connections,self.cur_connections, self.pools.qsize()))
            else:
                if self.pools.empty():
                    try:
                        c = CBClient(self.host, self.port, self.ioloop)
                        self.pools.put(c)
                    except:
                        logger.error(traceback.format_exc())

                conn = None
                try:
                    conn = self.pools.get(block=False)
                except Queue.Empty:
                    conn = None

                if conn:
                    self.cur_connections += 1
                    logger.debug("RpcConnectionPool: get_conn=%s", id(conn))

                logger.debug("RpcConnectionPool status: name=%s|max=%s|cur=%s|qsize=%s",\
                        self.name, self.max_connections, self.cur_connections, self.pools.qsize())
                return conn

    def free_conn(self, conn):
        with self.lock:
            logger.debug("RpcConnectionPool: try free=%s", conn)
            if conn:
                self.pools.put(conn)
                self.cur_connections -= 1
                logger.debug("RpcConnectionPool: free_conn=%s", id(conn))

class MaxConnections(Exception):
    pass


rpc_pools = {}

@contextmanager
def get_rpc_conn(rpc_name):
    pool = rpc_pools.get(rpc_name, None)
    if pool is None:
        import ews
        confs = JsonConfiger.get_instance().get("backends").get(rpc_name)
        pool = RpcConnectionPool(host=confs["host"], port=confs["port"], max_connections=confs["max_connections"], \
                                 rpc_name=rpc_name, ioloop=ews.current_ioloop())
        rpc_pools[rpc_name] = pool

    try:
        conn = pool.get_conn()
        yield conn
    except:
        # 捕获业务异常
        # 避免连接回收失败
        raise
    finally:
        pool.free_conn(conn)
