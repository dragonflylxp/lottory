# coding: utf-8
"""Easy Tornado
@author: ligx@500wan.com
@version: 0.1
@todo: add_handler考虑支持权值，方便使用者自行控制路由判断顺序
使用例子：
    import time
    import xtornado
    @xtornado.route_sync_func('/a')
    def aa(handler, *args, **kwargs):
        time.sleep(1)
        return 'hello'
    @xtornado.route_handler_class('/c')
    class cc(tornado.web.RequestHandler):
        def get(self, *args, **kwargs):
            self.write('world')
    xtornado.listen(8888)
    xtornado.start()
"""

from concurrent import futures

import tornado.web
import tornado.gen
import tornado.ioloop
import path
import traceback
import ews
import sys
from alert import AlertMoniter
from util.tools import Log
global logger
logger = Log().getLog()


web_application = tornado.web.Application([(r"/(.*)", tornado.web.StaticFileHandler, dict(path=path._STA_PATH)), ],template_path=path._TPL_PATH, debug=False)

def get_application():
    return web_application

def add_handler(*args):
    web_application.add_handlers('.*$', [args])

def listen(port, address=''):
    return web_application.listen(port, address)

def start():
    tornado.ioloop.IOLoop.current().start()

def stop():
    tornado.ioloop.IOLoop.current().stop()

def current_ioloop():
    return tornado.ioloop.IOLoop.instance()


def attach_periodic_callback(self, callback, callback_time):
    if self._periodic_callback is not None:
        self.dettach_periodic_callback()

    self._periodic_callback = ioloop.PeriodicCallback(callback, callback_time, self._ioloop)
    self._periodic_callback.start()

def dettach_periodic_callback(self):
    if self._periodic_callback is not None:
        self._periodic_callback.stop()
    self._periodic_callback = None




############################################################




MAX_THREADS = 16
thread_executor = futures.ThreadPoolExecutor(max_workers=MAX_THREADS)
thread_in_use = {}


class ThreadFuncHandler(tornado.web.RequestHandler):
    """for synchronize function call
    @author: ligx@500wan.com
    """

    _prepare_plugins = []
    _execute_plugins = []

    def initialize(self, route_path, exec_func):
        self.route_path = route_path
        self.exec_func = exec_func

    def prepare(self):
        # 获得正确的客户端ip
        ip = self.request.headers.get("X-Real-Ip", self.request.remote_ip)
        ip = self.request.headers.get("X-Forwarded-For", ip)
        ip = ip.split(',')[0].strip()
        self.request.remote_ip = ip
        # 负载判断
        if 100 * sum(thread_in_use.values()) / MAX_THREADS < 90:
            pass # 系统还能顶得住
        elif 100 * thread_in_use[self.route_path] / MAX_THREADS > 50:
            # 这个接口已经占用过多线程，返回系统忙（业务降级）
            self.send_error(503)
            return
        else:
            pass # todo: 随机返回服务忙？
        # 处理插件
        try:
            for func in self._prepare_plugins:
                func(self)
        except Exception as ex:
            params = {
                'trace_back': traceback.extract_tb(sys.exc_traceback),
                'exc_type': sys.exc_type,
                'exc_value': sys.exc_value,
                'servicename': self.request.host,
                "msgtype": "接口服务告警"

            }
            AlertMoniter().deal_exception_alert(params)
            logger.error('request failed(system error): [traceback=%s] [exc_type=%s] [exc_value=%s]',
                         params['trace_back'], params['exc_type'], params['exc_value'])
            raise ex #交给write_error处理


    @classmethod
    def prepare_plugin(cls):
        """给prepare添加一个函数插件（装饰器）
            注意：不要在插件里面进行任何的阻塞操作！
        @author: ligx@500wan.com
        """
        def deco_func(func):
            cls._prepare_plugins.append(func)
            return func
        return deco_func

    @tornado.gen.coroutine
    def handle(self, *args, **kwargs):
        """处理请求，在线程池里面排队执行并异步等待结果
        @author: ligx@500wan.com
        """
        try:
            thread_in_use[self.route_path] += 1 # route_path线程占用+1
            ret = yield thread_executor.submit(self.execute, *args, **kwargs)
            self.write(ret)
        finally:
            thread_in_use[self.route_path] -= 1 # route_path线程占用-1

    # 允许post、get、put、delete
    post = handle
    get = handle
    put = handle
    delete = handle

    def execute(self, *args, **kwargs):
        """处理请求，在执行之前先处理插件
        @author: ligx@500wan.com
        """
        for func in self._execute_plugins:
            func(self, *args, **kwargs)
        try:
            return self.exec_func(self, *args, **kwargs)
        except ews.EwsError as ex:
            logger.error('request failed(business error): [traceback=%s] [exc_type=%s] [exc_value=%s]',
                       traceback.extract_tb(sys.exc_traceback),sys.exc_type, ex.args[0])
            message = ews.get_status_msg(ex.args[0])
            if len(ex.args)>1: message = message % ex.args[1]
            return {'status':ex.args[0],
                    'message':message,
                    'data':{}}
        except Exception as ex:
            params = {
                'trace_back': traceback.extract_tb(sys.exc_traceback),
                'exc_type': sys.exc_type,
                'exc_value': sys.exc_value,
                'servicename': self.request.host,
                "msgtype": "接口服务告警",
                'path': self.route_path

            }
            AlertMoniter().deal_exception_alert(params)
            logger.error('request failed(system error): [traceback=%s] [exc_type=%s] [exc_value=%s]',
                         params['trace_back'], params['exc_type'], params['exc_value'])
            raise ex #交给write_error处理

    @classmethod
    def execute_plugin(cls):
        """给execute添加一个函数插件（装饰器）
        @author: ligx@500wan.com
        """
        def deco_func(func):
            cls._execute_plugins.append(func)
            return func
        return deco_func




############################################################




def route_sync_func(route_path, handler_class=ThreadFuncHandler):
    """给同步调用的函数使用的路由装饰器，接口将会在内置的线程池里面运行
    @author: ligx@500wan.com
    """
    def deco_func(exec_func):
        add_handler(route_path, handler_class, {
            'route_path': route_path,
            'exec_func': exec_func,
        })
        thread_in_use[route_path] = 0
        return exec_func # 做好登记就可以了，不需要修饰原来的函数功能
    return deco_func


def route_handler_class(route_path, **kwargs):
    """给tornado的handler类使用的路由装饰器，需要自己控制好同步和异步的问题
    @author: ligx@500wan.com
    """
    def deco_func(clazz):
        add_handler(route_path, clazz, kwargs)
        return clazz # 做好登记就可以了，不需要修饰原来的类
    return deco_func



