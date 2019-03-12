# coding: utf-8
"""Esun Web Service
@author: ligx@500wan.com
@version: 0.3
@todo: 解决非ThreadFuncHandler的prepare_json_args等问题
使用例子：
    import time
    import ews
    @ews.route_sync_func('/a')
    def aa(handler, *args, **kwargs):
        time.sleep(1)
        return 'hello'
    class bbbb(object):
        @ews.route_sync_func('/b', kwargs={ # 可以在这里登记参数和默认值，也为以后的文档自动化做准备
            'k1': ('v1', '这个地方是参数说明和注释'),
            'k2': (UserWarning, '这里表示没有默认参数，调用方必须传值'),
        })
        def bb(self, handler, *args, **kwargs):
            return handler.ok({'asdf': 'qwer'})
    @ews.route_handler_class('/c')
    class cccc(tornado.web.RequestHandler):
        def get(self, *args, **kwargs):
            self.write('world')
    ews.listen(8888)
    ews.start()
"""

import os
import sys
import atexit
import signal
import functools
import inspect
import imp
import copy
import glob
import traceback

import ujson
import tornado.ioloop
from tornado.log import access_log, app_log

import xtornado
from util.tools import Log

logger = Log().getLog()



STATUS_OK = '100'
STATUS_BUSY = '99'
STATUS_PARAM = '96'
STATUS_PARAM_ERROR = '97'
STATUS_ERROR = '101'
STATUS_SESSION_ERR = "102"
STATUS_LOGIN_PARAM = '105'
STATUS_LOGIN_ERROR = '103'
STATUS_LOGIN_NOT_REG = '104'
STATUS_LOGIN_FAIL = '105'
STATUS_USER_ACCOUNT_FAIL = '106'
STATUS_USER_INFO_FAIL = '107'
STATUS_PROJ_LIST_FAIL = '108'
STATUS_MULTI_LOGIN_ERR = "109"
STATUS_USER_MOBILE_ALREAD_REG = "110"
STATUS_USER_MOBILE_ACCOUNT_NOT_FOUND = "111"
STATUS_USER_SEND_SMS_FAIL = "112"
STATUS_USER_MOBILE_FORMAT_ERROR = "113"
STATUS_USER_REG_FAIL = "114"
STATUS_USER_SMS_CODE_ERROR = "115"
STATUS_USER_VERIDFY_CODE_LIMIT_ERROR = "116"
STATUS_USER_LOGIN_PASSWORD_ERROR = "117"
STATUS_USER_IMG_CODE_ERROR = "118"
STATUS_TRADE_CURRENT_EXPECT_ERROR = "119"
STATUS_LOTTERY_ISSUE_ERROR = "120"
STATUS_TRADE_PAY_ERROR = "121"
STATUS_TRADE_PROXY_ERROR = "122"
STATUS_PROJ_NOTFOUND = "123"
STATUS_RECHARGE_PLACE_ORDER_FAIL = "124"
STATUS_USER_NOT_AUTH = "125"
STATUS_CHASENUMBER_NOTFOUND = "126"

STATUS_USER_WITHDRAW_PLACEORDER_FAIL = "127"
STATUS_RECHARGE_SEARCH_FAIL = "128"
STATUS_AUTH_CHECK_TRUENAME = "129"
STATUS_AUTH_CHECK_IDCARD = "130"
STATUS_NOT_ADULT = "131"
STATUS_AUTH_TRUENAME_FAIL = "132"
STATUS_AUTH_NOT_MATCHING = "133"

STATUS_LOTTOCHECK_ERROR = "201"
STATUS_CHASENUMBER_LIST_FAIL = "134"
STATUS_USER_WITHDRAW_PLACEORDER_FAIL = "135"
STATUS_RECHARGE_SEARCH_FAIL = "136"
STATUS_USER_MOBILE_CODE_EMPTY ="137"
STATUS_USER_MOBILE_CODE_EXPIRE ="138"
STATUS_USER_MOBILE_CODE_ERROR ="139"
STATUS_USER_MOBILE_VERIFY_ERROR ="140"
STATUS_USER_PASSWORD_RESET_FAIL = "141"
STATUS_USER_PASSWORD_MODIFY_FAIL = "142"
STATUS_REALNAME_NOT_MATCHING_BANKCARD = "143"
STATUS_BIND_CARD_FAIL = "144"
STATUS_ALREADY_BIND_CARD = "145"
STATUS_ALREADY_TRUENAME = "146"
STATUS_AUTH_MOBILE_CODE_MULNUM = "147"
STATUS_COUPON_LIST_FAIL = "148"
STATUS_USER_PASSWORD_MODIFY_SAMEPWD = "149"
STATUS_NOT_BIND_CARD = "150"
STATUS_LOTTOCHECK_ERROR = "200"
STATUS_RPC_USER_ERROR = "201"
STATUS_RPC_ACCOUNT_ERROR = "202"
STATUS_RPC_TRADE_ERROR= "203"
STATUS_RPC_TICKET_ERROR = "204"
STATUS_RPC_ERROR = "205"
STATUS_PROJ_NOT_FOUND = "206"
STATUS_PROJ_FORBID_FOLLOW = "207"
STATUS_PROJ_DEADLINE = "208"
STATUS_PROJ_ALLMONEY_ERROR = "209"
STATUS_WITHDRAW_MONEY_LIMIT = "210"
STATUS_FOLLOW_HOT_SELLER_ERROR = "211"

status_msgs = {
    STATUS_OK : 'ok',
    STATUS_BUSY : '系统超负荷啦，攻城狮正忙着调资源，您先歇一会再试试啦~',
    STATUS_PARAM : 'bad or lack parameter',
    STATUS_PARAM_ERROR : '%s',
    STATUS_ERROR : '哦噢，系统开小差了，攻城狮正在修复中，您先歇一会再试试啦~',
    STATUS_LOGIN_PARAM: '用户名或密码为空',
    STATUS_LOGIN_ERROR: '用户名或密码错误',
    STATUS_LOGIN_NOT_REG: '用户未注册',
    STATUS_SESSION_ERR: "ck 失效",
    STATUS_LOGIN_FAIL: "登录失败",
    STATUS_USER_ACCOUNT_FAIL: "获取账户信息失败",
    STATUS_USER_INFO_FAIL: "获取用户信息失败",
    STATUS_PROJ_LIST_FAIL: "获取方案记录失败",
    STATUS_CHASENUMBER_LIST_FAIL: "获取追号记录失败",
    STATUS_COUPON_LIST_FAIL: "获取优惠券记录失败",
    STATUS_MULTI_LOGIN_ERR: "您的账号在其它设备登录了",
    STATUS_USER_MOBILE_ALREAD_REG: "帐号已存在，请直接登录",
    STATUS_USER_MOBILE_ACCOUNT_NOT_FOUND: "该手机号未注册",
    STATUS_USER_SEND_SMS_FAIL: "验证码发送错误",
    STATUS_USER_MOBILE_FORMAT_ERROR: "手机号格式错误",
    STATUS_USER_MOBILE_CODE_EMPTY: "验证码为空",
    STATUS_USER_MOBILE_CODE_EXPIRE: "验证码已过期",
    STATUS_USER_MOBILE_CODE_ERROR: "验证码错误",
    STATUS_USER_MOBILE_VERIFY_ERROR: "手机验证错误",
    STATUS_USER_PASSWORD_RESET_FAIL: "重置密码失败",
    STATUS_USER_PASSWORD_MODIFY_FAIL: "修改密码失败",
    STATUS_USER_PASSWORD_MODIFY_SAMEPWD: "新旧密码相同",
    STATUS_USER_REG_FAIL: "注册失败",
    STATUS_USER_SMS_CODE_ERROR: "验证码错误",
    STATUS_USER_VERIDFY_CODE_LIMIT_ERROR: "手机号存在安全隐患，请联系客服",
    STATUS_TRADE_PAY_ERROR: "%s",
    STATUS_TRADE_PROXY_ERROR: "调用交易服务异常",
    STATUS_USER_LOGIN_PASSWORD_ERROR: "账号或密码错误",
    STATUS_USER_IMG_CODE_ERROR: "验证码错误",
    STATUS_TRADE_CURRENT_EXPECT_ERROR: "当前期号错误",
    STATUS_LOTTERY_ISSUE_ERROR: "彩种期号获取失败",
    STATUS_PROJ_NOTFOUND: "方案不存在",
    STATUS_CHASENUMBER_NOTFOUND: "追号不存在",
    STATUS_LOTTOCHECK_ERROR: "投注格式错误:[%s]",
    STATUS_RPC_USER_ERROR: "用户服务错误:[%s]",
    STATUS_RPC_ACCOUNT_ERROR: "账户服务错误:[%s]",
    STATUS_RPC_TRADE_ERROR: "交易服务错误:[%s]",
    STATUS_RPC_TICKET_ERROR: "拆票服务错误:[%s]",
    STATUS_RECHARGE_PLACE_ORDER_FAIL: "充值下单失败",
    STATUS_USER_NOT_AUTH: "请实名认证",
    STATUS_USER_WITHDRAW_PLACEORDER_FAIL: '提款下单失败， 请联系客服',
    STATUS_RECHARGE_SEARCH_FAIL: "银行卡密码获取失败",
    STATUS_AUTH_CHECK_TRUENAME: "请填写真实姓名",
    STATUS_AUTH_CHECK_IDCARD : "请填写正确的身份证号",
    STATUS_NOT_ADULT: "网站不向未满18周岁的青少年出售彩票",
    STATUS_AUTH_TRUENAME_FAIL: "实名认证失败",
    STATUS_AUTH_NOT_MATCHING: "用户名身份证不匹配",
    STATUS_REALNAME_NOT_MATCHING_BANKCARD : "抱歉，银行卡号和实名信息不一致",
    STATUS_BIND_CARD_FAIL: "绑定银行卡失败",
    STATUS_ALREADY_BIND_CARD: "已经绑定银行卡",
    STATUS_ALREADY_TRUENAME: "已经实名认证",
    STATUS_AUTH_MOBILE_CODE_MULNUM: "单天获取验证码超过20次",
    STATUS_NOT_BIND_CARD: "请绑定银行卡，然后在提款",
    STATUS_RPC_ERROR: "%s",
    STATUS_PROJ_NOT_FOUND: "方案不存在",
    STATUS_PROJ_FORBID_FOLLOW: "该订单不能跟单",
    STATUS_PROJ_DEADLINE: "方案截止",
    STATUS_PROJ_ALLMONEY_ERROR: "方案金额错误",
    STATUS_WITHDRAW_MONEY_LIMIT: "提款金额不能小于1元",
    STATUS_FOLLOW_HOT_SELLER_ERROR: "获取大神信息失败"
}

def get_status_msg(st_code):
    return status_msgs.get(st_code) or \
            '火星报文[%s]。如果您看到了这个，请帮忙截屏给我们客服看看，谢谢！' % st_code


class EwsError(Exception):
    """自定义一个错误类，在业务代码里面raise这个类可以触发write_error输出统一格式的错误报文。"""
    pass




class ThreadFuncHandler(xtornado.ThreadFuncHandler):
    """for synchronize function call
    @author: ligx@500wan.com
    @todo: overwrite "log_exception"
    """

    def options(self, *args, **kwargs):
        # 允许跨域请求
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")

    def ok(self, data, extd=None):
        """组织处理成功的返回报文内容
        """
        if extd == 'verifycode':
            self.set_header('Content-Type', 'image/png; charset=UTF-8')
            self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")
            return data

        ret = {
            'status': STATUS_OK,
            'message': get_status_msg(STATUS_OK),
            'data': valuetostring(data),
        }
        if extd:
            ret['extd'] = extd


        logger.debug("[RESPONSE] PATH=%s|params=%s|resp=%s", self.route_path, self.json_args, data)
        ret = ujson.dumps(ret, ensure_ascii=False)
        if self.json_args.get('js_callback'):
            self.set_header('Content-Type', 'application/javascript; charset=UTF-8')
            self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")

            return '%s(%s)' % (self.json_args['js_callback'], ret)

        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")
            return ret

    def write_error(self, status_code=500, **kwargs):
        """覆盖原tornado的write_error，输出统一格式的错误报文。"""
        if status_code == 500:
            if "exc_info" in kwargs and isinstance(kwargs['exc_info'][1], EwsError):
                ex = kwargs['exc_info'][1]
                ret = {
                    'status': ex.args[0],
                    'message': get_status_msg(ex.args[0]),
                    'data': {},
                }
                if len(ex.args) > 1:
                    ret['message'] = ex.args[1] # 异常里面指定了给用户的反馈语
            else:
                ret = {
                    'status': STATUS_ERROR,
                    'message': get_status_msg(STATUS_ERROR),
                    'data': {},
                }
        else:
            ret = {
                'status': str(status_code),
                'message': get_status_msg(status_code),
                'data': {},
            }
            if 'err_msg' in kwargs:
                ret['message'] = ret['message'] % kwargs['err_msg']
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")
        self.finish(ujson.dumps(ret, ensure_ascii=False))


@ThreadFuncHandler.prepare_plugin()
def allow_cross_site(handler):
    # 允许跨域请求
    req_origin = handler.request.headers.get("Origin")
    if req_origin:
        handler.set_header("Access-Control-Allow-Origin", req_origin)
        handler.set_header("Access-Control-Allow-Credentials", "true")
        handler.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type, Custom-Params")
        handler.set_header("Allow", "GET, HEAD, POST")


@ThreadFuncHandler.prepare_plugin()
def prepare_json_args(handler):
    """分析请求参数
    @author: ligx@500wan.com
    """
    # 初始化默认参数
    customparams = handler.request.headers.get("Custom-Params", {})
    logger.info(handler.request.headers)
    public_args = {}
    if customparams:
        public_args = ujson.loads(customparams)
    json_args = dict((k, v[0]) for k, v in route_entries.get(handler.route_path)['kwargs'].items())
    type_args = dict((k, v[-1]) for k, v in route_entries.get(handler.route_path)['kwargs'].items())
    # 处理用户输入的参数
    if handler.request.headers.get('Content-Type', '').find("application/json") >= 0:
        # json格式请求
        try:
            user_args = ujson.loads(handler.request.body)
        except Exception as ex:
            logger.debug(traceback.format_exc())
            handler.write_error(STATUS_PARAM_ERROR, "参数解析错误")
            return
    else:
        # 普通参数请求
        user_args = dict((k, v[-1]) for k, v in handler.request.arguments.items())
    # 参数检查

    json_args.update(public_args)
    json_args.update(user_args)
    logger.debug("[REQUEST] PATH=%s|params=%s", handler.route_path, json_args)
    for k, v in json_args.items():
        if v == UserWarning:
            # 有必填参数未传值
            handler.write_error(STATUS_PARAM_ERROR, err_msg="参数[{}]未传".format(k))
            return
        elif type_args.get(k, '') == 'int':
            try:
                int(v)
            except:
                handler.write_error(STATUS_PARAM_ERROR, err_msg="参数[{}]必须为整型".format(k))
        elif type_args.get(k, '') == 'float':
            try:
                float(v)
            except:
                handler.write_error(STATUS_PARAM_ERROR, err_msg="参数[{}]必须为浮点型".format(k))
                return
        elif type_args.get(k, '') == 'unsigned int':
            try:
                if int(v) < 0:
                    handler.write_error(STATUS_PARAM_ERROR, err_msg="参数[{}]必须为非负整型".format(k))
            except:
                handler.write_error(STATUS_PARAM_ERROR, err_msg="参数[{}]必须为非负整型".format(k))
    handler.json_args = json_args




############################################################




route_handler_class = xtornado.route_handler_class
listen = xtornado.listen
stop = xtornado.stop
get_application = xtornado.get_application
add_handler = xtornado.add_handler
current_ioloop = xtornado.current_ioloop

route_entries = {}
def route_sync_func(route_path, handler_class=ThreadFuncHandler, kwargs={}):
    """扩展xtornado的route_sync_func，支持对class的method做修饰。
    由于被修饰的class在修饰method在这里还没处于可用状态，要到start的时候才延时载入
    @author: ligx@500wan.com
    """
    if route_path[0] != '/':
        route_path = '/' + route_path
    def deco_func(exec_func):
        route_entries[route_path] = {
            'route_path': route_path,
            'class_name': inspect.stack()[1][3],
            'exec_func': exec_func,
            'handler_class': handler_class,
            'doc': exec_func.__doc__,
            'kwargs': kwargs,
        }
        return exec_func # 做好登记就可以了，不需要修饰原来的函数功能
    return deco_func


def load_biz_dir(dir_path):
    """载入biz_dir目录里面的所有py文件，主要是为了方便route_sync_func等业务自动注册
    @author: ligx@500wan.com
    """
    for fname in os.listdir(dir_path):
        # if fname[0] in '._':
        #     continue
        if fname[-3:] != '.py':
            continue
        fpath = os.path.join(dir_path, fname)
        if not os.path.isfile(fpath):
            continue
        imp.load_source('_biz_' + fname[:-3], fpath)


stop_plugins = []
def add_stop_plugin(func, *args, **kwargs):
    stop_plugins.append([func, args, kwargs])
# 注册SIGTERM信号处理
signal.signal(signal.SIGTERM, lambda signum, frame: xtornado.stop())


def start():
    # 登记xtornado路由
    def local_func(exec_func, route_path, handler_class):
        @xtornado.route_sync_func(route_path, handler_class)
        def deco_func(*args, **kwargs):
            return exec_func(*args, **kwargs)
    for route_info in route_entries.values():
        if route_info['class_name'] == '<module>':
            exec_func = route_info['exec_func']
        else:
            # 给method做修饰的时候，method所属的class还没处于可用状态，延迟到这里才生成对象
            cls = getattr(sys.modules[route_info['exec_func'].__module__], route_info['class_name'])
            exec_func = getattr(cls(), route_info['exec_func'].__name__)
        # 录入到xtornado
        local_func(exec_func, route_info['route_path'], route_info['handler_class'])
    # todo: 远程注册服务，定时心跳通知
    # 开始服务
    get_application().settings['log_function'] = log_function
    xtornado.start()
    # 调用停止服务需要执行的插件
    for plg in stop_plugins:
        try:
            plg[0](*plg[1], **plg[2])
        except Exception as ex:
            app_log.exception('something wrong when stopping: {0}'.format(plg[0]))


def log_function(handler):
    """记录请求日志
    """
    if handler.get_status() < 400:
        log_method = access_log.info
        log_method2 = app_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
        log_method2 = app_log.warning
    else:
        log_method = access_log.error
        log_method2 = app_log.error
    req = handler.request
    log_method('%s "%s" %d %s %.6f',
               req.method, req.uri, handler.get_status(),
               req.remote_ip, req.request_time() )
    # log_method2('%s %s %s %.6f',
    #             req.path, handler.current_user, handler.json_args,
    #             req.request_time() )



def valuetostring(d):
    """遍历结果数据dict,将value转为string
    """
    if isinstance(d, list):
        for i in xrange(len(d)):
            dd = d[i]
            d[i] = valuetostring(dd)
    elif isinstance(d, dict):
        for k, v in d.iteritems():
            d[k] = valuetostring(v)
    else:
        if d == None:
            return d
        if isinstance(d, unicode):
            d = d.encode('utf-8')
        d = str(d)
    return d
