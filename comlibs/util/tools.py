# coding=utf-8
import re
import socket
import fcntl
import struct
import urllib
import base64
import hashlib
import inspect
import logging
import logging.config
import threading
import traceback
import uuid
import xml.sax
import xml.sax.handler

import datetime
import curl
import ujson
import xml_util
import requests
import time
import os
import sys
import path
import yaml


reload(sys)
sys.setdefaultencoding('utf-8')


class Log():
    logger = None

    @classmethod
    def set_up(cls, log_cnf, port=''):
        with open(log_cnf['config_file']) as f:
            cfg = yaml.load(f)
            for k, v in cfg.get("handlers", {}).iteritems():
                if 'filename' in v:
                    suffix = "_" + str(port) if port else ''
                    v['filename'] = v['filename'] % suffix
            logging.config.dictConfig(cfg)
        Log.logger = logging.getLogger(log_cnf['default_logger'])

    def getLog(self):
        if Log.logger is None:
            Log.logger = logging.getLogger('simple')
        return Log.logger

class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        self.mapping[name] = self.buffer

    def getDict(self):
        return self.mapping


class RequestXml:
    @ staticmethod
    def http_request_get(url, params=None, timeout=3):
        try:
            t1 = time.time()
            xml = requests.get(str(url), params, timeout=timeout)
            t2 = time.time()
            Log().getLog().info("url=%s|spendTime=%s", url, (t2 - t1))
            return xml
        except:
            Log().getLog().exception("==== url[%s] ====", url)
            raise
        finally:
            pass

    @staticmethod
    def get_xml_dom(url, params=None, timeout=3):
        try:
            url = url.encode("utf-8")
        except Exception as ex:
            url = str(url)
            Log().getLog().error(ex)

        xml = RequestXml.http_request_get(url, params=params, timeout=timeout)
        try:
            dom = xml_util.parse_xml(xml.text.encode('utf-8'))
        except Exception as e:
            Log().getLog().info((url, e))
            raise e
        return dom

    @staticmethod
    def get_json(url, params=None, encode="utf-8", timeout=3):
        if encode:
            url = url.encode(encode)
        json_str = RequestXml.http_request_get(url, params=params, timeout=timeout)
        json_str = json_str.text
        try:
            data = ujson.loads(json_str)
        except Exception as e:
            Log().getLog().exception("----%s", url)
            raise e
        return data


class Profiler:
    clicks = {}

    @staticmethod
    def time_cost(func):
        def wrapper(*args, **kwargs):
            tid = threading.current_thread().ident
            key = str(tid) + func.__name__
            ret = func(*args, **kwargs)
            Log().getLog().debug("Profiler Time cost: func_name=%s|ret=%s", func.__name__, ['t{}-t{}={}'.format(
                idx + 1, idx, Profiler.clicks[key][idx] - Profiler.clicks[key][idx - 1]) for idx, k in enumerate(Profiler.clicks[key]) if idx > 0])
            Profiler.clicks[key] = []
            return ret
        return wrapper

    @staticmethod
    def click(fname):
        tid = threading.current_thread().ident
        key = str(tid) + fname
        if key in Profiler.clicks:
            Profiler.clicks[key].append(time.time())
        else:
            Profiler.clicks[key] = [time.time()]

    @staticmethod
    def curfunc_name():
        return inspect.stack()[1][3]


class CurlHttpRequest(object):
    '''发送http相关请求
    '''

    @staticmethod
    def post(url, timeout=8, params={}):
        cc = None
        try:
            t1 = time.time()
            cc = curl.Curl()
            cc.set_timeout(timeout)
            resp = cc.post(str(url), params)
            t2 = time.time()
            t = t2 - t1
            Log.logger.info(
                "curlHttpPost|url=%s|params=%s|resp=%s|spendTime=%f", url, params, resp, t)
            return resp
        except:
            Log.logger.error("curl tcm api interface error %s |params %s", url, params)
            Log.logger.error(traceback.format_exc())
            raise requests.exceptions.ConnectTimeout
        finally:
            if cc:
                cc.close()

    @staticmethod
    def get(url, timeout=8, params=None, return_codeing="utf8"):
        '''
            注意,如果返回的报文内容较大, 请勿使用, 因为日志打印了resp
            @params: timeout 超时时间
            @params: params 请求参数
        '''
        try:
            t1 = time.time()
            cc = curl.Curl()
            cc.set_timeout(timeout)
            resp = cc.get(str(url), params)
            if return_codeing != "utf8":
                resp = resp.decode(return_codeing)

            if not params:
                params = {}

            t2 = time.time()
            Log.logger.info("curlHttpRequest|url=%s|timeout=%s|params=%s|resp=%s|spendtime=%f", url,
                            timeout, urllib.urlencode(params), resp[:200], (t2 - t1))
            return resp
        except:
            Log.logger.error("curl tcm api interface error %s |params %s", url, params)
            Log.logger.error(traceback.format_exc())
            raise requests.exceptions.ConnectTimeout
        finally:
            cc.close()




def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def compare_version(ver1, ver2):
    """版本号比较
    """
    if not ver1:
        return -1
    if not ver2:
        return 1
    ver1a = [int(i) for i in ver1.split('.')[:3]]
    ver2a = [int(i) for i in ver2.split('.')[:3]]
    if ver1a == ver2a:
        return 0
    elif ver1a > ver2a:
        return 1
    else:
        return -1

def detailtrace(info):
    retStr = ""
    f = sys._getframe()
    f = f.f_back
    while hasattr(f, "f_code"):
        co = f.f_code
        retStr = "%s(%s:%s)->" % (os.path.basename(co.co_filename), co.co_name, f.f_lineno) + retStr
        f = f.f_back
    return retStr + info

