# encoding: utf-8
import time
import MySQLdb
from model.dao import MongoDataModel
from dbpool import db_pool
from util.tools import Log

logger = Log().getLog()

class BaseModel(object):
    def __init__(self):
        self.conn_r = db_pool.get_mysql("nncp_ro")
        self.conn_w = db_pool.get_mysql("nncp_wr")
        self.conn = db_pool.get_mysql("nncp")
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        self.rds = db_pool.get_redis("msgbus")
        self.mongo = MongoDataModel()

    def __del__(self):
        if self.conn: self.conn.close()

def access(level, cursor='dict'):
    def _wrapper(f):
        def __wrapper(*args, **kwargs):
            obj = args[0]
            if level == 'r':
                setattr(obj, 'conn', getattr(obj, 'conn_r'))
            elif level == 'w':
                setattr(obj, 'conn', getattr(obj, 'conn_w'))
            else:
                pass  # default attribute

            if cursor == 'list':
                setattr(obj, 'cursor', obj.conn.cursor())
            else:
                setattr(obj, 'cursor', obj.conn.cursor(MySQLdb.cursors.DictCursor))
            return f(*args, **kwargs)

        return __wrapper

    return _wrapper


class ExampleModel(BaseModel):
    """
    This ExampleModel will show you how to use the BaseModel
    see Api at `crazy-bet/biz/test_base_model.py`
    """

    @access('r', cursor='list')
    def login(self, uid, name):
        sql = """
            SELECT *
            FROM t_gold_account
            WHERE f_uid=%s
        """
        data = {}
        try:
            self.cursor.execute(sql, (uid,))
            data = self.cursor.fetchone()
        except:
            self.conn.rollback()
        return data

    @access('w')
    def logout(self, uid, name):
        sql = """
            SELECT *
            FROM t_gold_account
            WHERE f_uid=%s
        """
        data = {}
        try:
            self.cursor.execute(sql, (uid,))
            data = self.cursor.fetchone()
        except:
            self.conn.rollback()
        return data

    @access('rw')
    def register(self, uid, name):
        sql = """
            SELECT *
            FROM t_gold_account
            WHERE f_uid=%s
        """
        data = {}
        try:
            self.cursor.execute(sql, (uid,))
            data = self.cursor.fetchone()
        except:
            self.conn.rollback()
        return data

    @access('w', cursor='list')
    def unregister(self, uid, name):
        sql = """
            SELECT *
            FROM t_gold_account
            WHERE f_uid=%s
        """
        data = {}
        try:
            self.cursor.execute(sql, (uid,))
            data = self.cursor.fetchone()
        except:
            self.conn.rollback()
        return data
