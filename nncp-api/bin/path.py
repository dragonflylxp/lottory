#coding=utf-8
import os
import sys


_HOME_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_BIN_PATH = os.path.join(_HOME_PATH, 'bin')
_BIZ_PATH = os.path.join(_HOME_PATH, 'biz')
_ETC_PATH = os.path.join(_HOME_PATH, 'etc')
_LIB_PATH = os.path.join(_HOME_PATH, 'lib')
_STA_PATH = os.path.join(_HOME_PATH, 'static')
_WEBSOCK_PATH = os.path.join(_HOME_PATH, 'websock')
_JOB_PATH = os.path.join(_HOME_PATH, 'jobs')
_TPL_PATH = os.path.join(_HOME_PATH, 'templates')
_DAT_PATH = os.path.join(_HOME_PATH, 'data')
_TEST_PATH = os.path.join(_HOME_PATH, 'tests')
_COM_PATH = os.path.join(os.path.dirname(_HOME_PATH), 'comlibs')


_path = ()
_path += _BIN_PATH, _BIZ_PATH, _ETC_PATH, _LIB_PATH, _STA_PATH, _WEBSOCK_PATH, _JOB_PATH, _TPL_PATH, _TEST_PATH, _COM_PATH
map(sys.path.append, _path)

