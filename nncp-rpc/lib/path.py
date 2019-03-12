#coding=utf-8
import os
import sys


_HOME_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_BIN_PATH = os.path.join(_HOME_PATH, 'bin')
_BIZ_PATH = os.path.join(_HOME_PATH, 'biz')
_MSG_PATH = os.path.join(_HOME_PATH, 'msg')
_ETC_PATH = os.path.join(_HOME_PATH, 'etc')
_LIB_PATH = os.path.join(_HOME_PATH, 'lib')
_COM_PATH = os.path.join(os.path.dirname(_HOME_PATH), 'comlibs')

_path = ()
_path += _BIN_PATH, _BIZ_PATH, _MSG_PATH, _ETC_PATH, _LIB_PATH, _COM_PATH
map(sys.path.append, _path)

