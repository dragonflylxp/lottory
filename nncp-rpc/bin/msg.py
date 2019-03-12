#encoding=utf-8

import os
import sys
import argparse
import ujson
import signal
import traceback
import imp
import tornado
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'lib'))

import path
from cbrpc import CBClient,CBServer
import xmsgbus
import wsclient
from msgbus import rmq
from util.tools import Log
from util.configer import *
from dbpool import db_pool

def init(conf_file, svr_type='', port=''):
    #载入配置文件
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    confs = JsonConfiger.get_instance()
    confs.load_file(conf_file)

    #初始化日志
    log_cnf = confs.get('logging')
    if log_cnf['config_file'][:1] not in ['/', '\\']:
        log_cnf['config_file'] = os.path.join(os.path.dirname(os.path.abspath(conf_file)),log_cnf['config_file'])
    Log.set_up(log_cnf, port)
    global logger
    logger = Log().getLog()

    #初始化db
    db_pool.set_up(confs.get("database"))

    #初始化mq
    xmsgbus.set_up(confs)
    rmq.setup_producer(confs.get("mq/rabbitmq"))
    #rmq.setup_consumer(confs.get("mq/rabbitmq/"+svr_type))


def load_msg():
    #注册消息业务
    for fname in os.listdir(path._MSG_PATH):
        if fname[-3:] != '.py':
            continue
        fpath = os.path.join(path._MSG_PATH, fname)
        imp.load_source('_msg_'+fname[:-3], fpath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('MSGServer cmd options:')
    parser.add_argument('-c', default=os.path.join(path._ETC_PATH, 'includes_dev.json'),help="-c cfgfile ******加载配置文件")
    args = parser.parse_args();

    #初始化服务
    try:
        init(args.c)
        load_msg()
    except Exception,e:
        print 'Init error: %s' % e
        print traceback.format_exc()
        sys.exit(0)
    logger.info("MSG Server starting..., configurated by (%s)", args.c)

    #启动服务
    logger.info("MSG Server started!")
    try:
        xmsgbus.attach(tornado.ioloop.IOLoop.current())
        #if rmq.rmq_consumer: rmq.rmq_consumer.attach(tornado.ioloop.IOLoop.current())
    except:
        logger.error(traceback.format_exc())
    tornado.ioloop.IOLoop.current().start()
