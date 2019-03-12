#encoding=utf-8

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'lib'))
import path
from cbrpc import CBClient,CBServer
import traceback


uinfo = dict()
c = CBClient('127.0.0.1',7003)

print c.call('hello','li')
try:
    c.call('bad')
except:
    print 'A exception occurs in svr!'
