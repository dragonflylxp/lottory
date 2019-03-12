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
import wsclient
from msgbus import rmq
from util.tools import Log
from util.configer import *
from dbpool import db_pool
from aliyun import sms

def init(conf_file, svr_type, port=''):
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
    rmq.setup_producer(confs.get("mq/rabbitmq"))
    # sms.set_up(confs.get("aliyun"))
    #rmq.setup_consumer(confs.get("mq/rabbitmq/"+svr_type))


def load_biz(svr_type):
    #注册业务接口
    imp.load_source('interfaces','/'.join([path._BIZ_PATH,svr_type,'interfaces.py']))

signal.signal(signal.SIGTERM, lambda signum,frame: rpcsvr.stop())
if __name__ == "__main__":
    parser = argparse.ArgumentParser('RPCServer cmd options:')
    parser.add_argument('-c', default=os.path.join(path._ETC_PATH, 'includes_dev.json'),help="-c cfgfile ******加载配置文件")
    parser.add_argument('-p', type=int, default=4242,help="-p port ******启动端口")
    parser.add_argument('-t', default='Demo',help="-t type ******服务类型")
    args = parser.parse_args();

    #初始化服务
    try:
        init(args.c, args.t, args.t+str(args.p))
        load_biz(args.t)
    except Exception,e:
        print 'Init error: %s' % e
        print traceback.format_exc()
        sys.exit(0)
    logger.info("%sServer starting..., listen [%d], configurated by (%s)",args.t,args.p,args.c)

    #启动服务
    logger.info("%sServer started!",args.t)
    rpcsvr = CBServer(sys.modules.get('interfaces').Interfaces(), args.p)
    try:
        wsclient.attach(rpcsvr.current_ioloop())
        #if rmq.rmq_consumer: rmq.rmq_consumer.attach(rpcsvr.current_ioloop())
    except:
        logger.error(traceback.format_exc())
    rpcsvr.start()
