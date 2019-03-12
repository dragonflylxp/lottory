# coding: utf-8

import os
import sys
import argparse
reload(sys)
sys.setdefaultencoding("utf-8")
os.environ['BASIC_PATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.environ['BASIC_PATH'], 'lib'))

import ews
import job
import path
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from util import color
import jiuzhao
import lianlian


def init(conf_file, port=''):
    #载入配置文件
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    confs = JsonConfiger.get_instance()
    confs.load_file(conf_file)

    #初始化日志
    log_cnf = confs.get('logging')
    if log_cnf['config_file'][:1] not in ['/', '\\']:
        log_cnf['config_file'] = os.path.join(
            os.path.dirname(os.path.abspath(conf_file)), log_cnf['config_file'])
    Log.set_up(log_cnf, port)
    global logger
    logger = Log().getLog()
    jiuzhao.set_up(confs.get("jiuzhao"))
    lianlian.set_up(confs.get("lianlian"))

    #加载业务代码
    ews.load_biz_dir(path._JOB_PATH)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('EWS cmd options:')
    parser.add_argument('-c', default=os.path.join(
        path._ETC_PATH, 'includes_dev.json'), help="-c cfgfile ******加载配置文件")
    args = parser.parse_args()
    init(args.c)
    job.attach(ews.current_ioloop())
    ews.start()
