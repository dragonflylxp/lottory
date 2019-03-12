#coding:utf-8
import pytz
import traceback
from bson import *
from pymongo import collection
from pymongo.bulk import BulkOperationBuilder
from dbpool import db_pool
from util.tools import Log

logger = Log().getLog()

class MongoDataModel(object):
    """mongodb dao
    """
    def __init__(self):
        client = db_pool.get_mongo('nncp')
        self.db = client.get_default_database()

    def find(self, table, SON=None, pn=0, rn=0, sort=None, count=False, projection=None):
        try:
            data = []
            col = collection.Collection(self.db, table)
            #修改时区UTC->local time zone
            col = col.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('Asia/Shanghai')))
            cur = col.find(filter=SON,projection=projection, skip=pn*rn, limit=rn, sort=sort)
            for doc in cur:
                #将ObjectId转为str
                if doc.has_key("_id"):
                    doc["_id"] = str(doc["_id"])
                #日期格式化
                if doc.has_key("crtime") and isinstance(doc['crtime'],datetime.datetime):
                    doc["crtime"] = doc['crtime'].strftime('%Y-%m-%d %H:%M:%S')
                data.append(doc)
            #若要计数，则将计数添加在列表末尾
            if count:
               data.append(col.count(SON))
            return data
        except Exception as e:
            logger.error(traceback.format_exc())
            return []

    def find_and_modify(self, table, SON, DOC, upsert=True, multi=False):
        """
        """
        try:
            col = collection.Collection(self.db, table)
            if not multi:
                col.find_and_modify(SON, DOC, upsert)
        except Exception as e:
            logger.error(traceback.format_exc())

    def insert(self, table, DOC):
        ret = None
        try:
            col = collection.Collection(self.db, table)
            if isinstance(DOC, dict):
                ret = col.insert_one(DOC)
            elif isinstance(DOC, list):
                ret = col.insert_many(DOC)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return ret

    def update(self, table, SON, DOC, upsert=False, multi=False):
        try:
            col = collection.Collection(self.db, table)
            if not multi:
                col.update_one(SON, DOC, upsert)
            else:
                col.update_many(SON, DOC, upsert)
        except Exception as e:
            logger.error(traceback.format_exc())

    def remove(self, table, DOC, multi=True):
        try:
            col = collection.Collection(self.db, table)
            if not multi:
                col.delete_one(DOC)
            else:
                col.delete_many(DOC)
        except Exception as e:
            logger.error(traceback.format_exc())

    def count(self, table, SON={}, **kwargs):
        try:
            col = collection.Collection(self.db, table)
            return col.count(SON, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            return 0

    """批量更新接口
    """
    def bulk_upsert_operation(self, table, SON, DOC):
        try:
            col = collection.Collection(self.db, table)
            bulkop = BulkOperationBuilder(col, ordered=False)
            bulkop.find(SON).update(DOC)
            return bulkop.execute()
        except Exception as e:
            logger.error(traceback.format_exc())
            return None

    def find_one(self, table, SON={}, pn=0, rn=0, sort=None, count=False):
        try:
            data = {}
            col = collection.Collection(self.db, table)
            #修改时区UTC->local time zone
            col = col.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('Asia/Shanghai')))
            data = col.find_one(filter=SON, skip=pn*rn, limit=rn, sort=sort)
            return data
        except Exception as e:
            logger.exception(e)
            return {}

