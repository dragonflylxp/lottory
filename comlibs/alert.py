# coding=utf-8

import time
import Queue
import uuid

from dbpool import db_pool
from util.tools import Log
from wechat.Monitor import send_textcard_message
import ujson
from aliyun import sms
import traceback
logger = Log().getLog()

configs = {}
alert_queue = Queue.Queue(10)


def set_up(confs):
    configs.update(confs)

NNCP_ALERT_QUEUE = "nncp:alert:queue"
class AlertMoniter(object):
    """报警处理函数
    """
    def __init__(self):
        self.rds = db_pool.get_redis('main')


    def deal_exception_alert(self, params):
        """处理框架异常告警
        """
        trace_back = params.get('trace_back', '')[2:]
        exc_type = params.get('exc_type', '')
        exc_value = params.get('exc_value', '')
        interface_path = params.get("path", "")

        msg = "接口地址：{}</br>异常信息：exc_value:{}<br> traceback:{} <br> exc_type={}".format(
            interface_path, exc_value, trace_back, exc_type)
        info = {}
        info.update(params)
        info.update({
            "msg": msg
        })
        self.add_alert_msg(info, biztype='exception')

    def get_alert_switch(self):
        """获取开关
        """
        alert_config = {"switch": 1}
        return alert_config


    def add_alert_msg(self, msg, level=1, biztype=''):
        """添加告警信息，如果告警阻塞则抛弃
        params:
        msg:告警信息
        level:告警级别
        """
        try:
            alert_config = self.get_alert_switch()
            if msg and alert_config.get('switch') == 1:
                self.rds.rpush(NNCP_ALERT_QUEUE, ujson.dumps(msg))
                return 1
            return 0
        except:
            logger.exception('alert blocking')
            return 0

    def send_alert(self):
        """发送报警信息
        """
        alert_msg = ""
        try:
            alert_msg = self.rds.lpop(NNCP_ALERT_QUEUE)
            if alert_msg:
                self.send_msg(alert_msg)
            else:
                pass
        except Exception as ex:
            logger.exception((alert_msg, ex))

    def send_msg(self, msg):
        """发送
        """
        try:
            alert_msg = ujson.loads(msg)
            print alert_msg
            servicename = alert_msg.get("servicename", "ews-api")
            msgtype = alert_msg.get("msgtype", "服务告警")
            msg = alert_msg.get("msg", "except")
            send_textcard_message(msgtype=msgtype, servicename=servicename, exceptinfo=msg)
        except:
            logger.error(traceback.format_exc())
            params = {
                "code": "告警服务异常"
            }
            sms.send_sms(uuid.uuid1(), "13319403331", "小牛", "SMS_127035066", ujson.dumps(params))

