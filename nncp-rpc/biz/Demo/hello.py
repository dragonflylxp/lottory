#encoding=utf-8

import inspect
import MySQLdb
import traceback
from dbpool import db_pool
from util.tools import Log
from util.configer import *

logger = Log().getLog()

def get_current_function_name():
    return inspect.stack()[1][3]

#Hello word
class HelloBiz(object):
    def hello(self, name):
        """write service document here
        """
        logger.debug('hello')
        logger.info('Remote process call:%s',get_current_function_name())
        return "Hello, %s too" % name

#服务端异常可抛给客户端捕获
class ExceptionBiz(object):
    def bad(self):
        raise Exception('Exception occurs in Server!')

#作为客户端访问后端服务
class BackendBiz(object):
    def callbackend(self, name):
        logger.info('Remote process call:%s',get_current_function_name())
        usercfg = JsonConfiger.get_instance().get("backends").get("UserSvr")
        UserSvr = CBClient(usercfg.get("host"),usercfg.get("port"))
        return UserSvr.call('get_second_name','li')

#mysql
class MysqlDemo(object):
    def select(self):
        conn = None
        ret = {}
        try:
            conn = db_pool.get_mysql("crazy_bet")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM t_user LIMIT 1"
            cursor.execute(sql)
            ret = cursor.fetchone() or {}
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e #抛出异常给客户端捕获
        finally:
            if conn: conn.close()
            return ret

#redis
class RedisDemo(object):
    def get(self,key):
        rds = db_util.get_redis('main')
        return rds.get(key)
