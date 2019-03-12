#encoding=utf-8
from Demo.hello import HelloBiz,ExceptionBiz

"""收集业务类方法作为RPC总入口
"""
class Interfaces(object):

    def hello(self,name):
        return HelloBiz().hello(name)

    def bad(self):
        raise ExceptionBiz().bad()
