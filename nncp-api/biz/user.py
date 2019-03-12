# coding: utf-8
import random

import ews
import time
from cbrpc import CBClient
from util.configer import *
import traceback
import session
import ujson
from hook import Hook
from commonEntity.User import UserBean
from dbpool import db_pool
import rediskey
import define
from gen_verify_code import get_img, get_img_url

@ews.route_sync_func('/user/login', kwargs={'mobile': (UserWarning, 'string'), 'password': (UserWarning, 'string')})
@Hook.post_hook('user_login')
def login(handler, *args, **kwargs):
    mobile = handler.json_args.get("mobile", "")
    password = handler.json_args.get("password", "")
    login_type = handler.json_args.get("logintype", "mobile")
    platform = handler.json_args.get("platform", "")
    channel = handler.json_args.get("channel", "")
    subchannel = handler.json_args.get("subchannel", "")
    ip = handler.request.remote_ip
    ua = handler.request.headers.get("User-Agent", "")
    mbimei = handler.json_args.get("mbimei", "")
    verifycode = handler.json_args.get("verifycode", "")
    params = {
        "mobile": mobile,
        "password": password,
        "login_type": login_type,
        "mbimei": mbimei,
        "platform": platform,
        "channel": channel,
        "subchannel": subchannel,
        "ip": ip,
        "ua": ua,
        "verifycode": verifycode

    }
    ret = UserBean().user_login(params)
    return handler.ok(ret)


@ews.route_sync_func('/user/account', kwargs={'ck': (UserWarning, 'string')})
def user_account(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')

    params = {
        "uid": uid
    }
    ret = UserBean().user_account(params)

    return handler.ok(ret)


@ews.route_sync_func('/user/info' , kwargs={'ck': (UserWarning, 'string')})
def user_info(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')

    params = {
        "uid": uid
    }
    ret = UserBean().user_info(params)
    return handler.ok(ret)


@ews.route_sync_func('/user/reg', kwargs={'mobile': (UserWarning, 'string')})
@Hook.post_hook('user_reg')
def user_reg(handler, *args, **kwargs):
    params = {
        "mobile": handler.json_args.get("mobile", ""),
        "password": handler.json_args.get("password", ""),
        "code": handler.json_args.get("code", ""),
        "type": handler.json_args.get("regtype", ""),
        "platform": handler.json_args.get("platform", ""),
        "channel": handler.json_args.get("channel", ""),
        "subchannel": handler.json_args.get("subchannel", ""),
        "deviceid": handler.json_args.get("deviceid", ""),
        "ip": handler.request.remote_ip,
        "ua": handler.request.headers.get("User-Agent", ""),
        "idfa": handler.json_args.get("idfa", ""),
        "channel": handler.json_args.get("channel", "")
    }
    regtype = handler.json_args.get("regtype", "mobile")
    if regtype == "mobile":
        info = UserBean().user_mobile_reg(params)
        return handler.ok(info)



@ews.route_sync_func('/user/account/detail', kwargs={'ck': (UserWarning, 'string')})
def user_account_detail(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")
    biztype=  handler.json_args.get("biztype", "0")
    params = {
        "uid": uid,
        "pageno": pageno,
        "pagesize": pagesize,
        "biztype": biztype
    }
    ret = UserBean().user_account_detail(params)
    return handler.ok(ret)


@ews.route_sync_func('/user/reg/send_sms', kwargs={'mobile': (UserWarning, 'string'),
                                                    'vtype': (UserWarning, 'string')})
def reg_send_sms(handler, *args, **kwargs):
    mobile = handler.json_args.get("mobile")
    vtype = handler.json_args.get("vtype", "reg")

    ret = UserBean().user_send_sms(mobile, vtype)
    return handler.ok(ret)

@ews.route_sync_func('/user/reg/verify_sms', kwargs={'mobile': (UserWarning, 'string'),
                                                    'code': (UserWarning, 'string')})
def reg_verify_sms(handler, *args, **kwargs):
    mobile = handler.json_args.get("mobile")
    code = handler.json_args.get("code", "0")
    ret = UserBean().user_verify_sms(mobile, code)
    return handler.ok(ret)

@ews.route_sync_func('/user/password/reset', kwargs={'mobile': (UserWarning, 'string'),
                                                    'code': (UserWarning, 'string'),
                                                    'checksum': (UserWarning, 'string'),
                                                    'password': (UserWarning, 'string')})
def user_password_reset(handler, *args, **kwargs):
    """短信验证后重置密码
    """
    mobile = handler.json_args.get("mobile")
    code = handler.json_args.get("code", "0")
    checksum = handler.json_args.get("checksum")
    password =  handler.json_args.get("password")
    status = UserBean().user_password_reset(mobile, code, checksum, password)
    return handler.ok({"status": status})

@ews.route_sync_func('/user/password/modify', kwargs={'mobile': (UserWarning, 'string'),
                                                    'code': (UserWarning, 'string'),
                                                    'checksum': (UserWarning, 'string'),
                                                    'oldpassword': (UserWarning, 'string'),
                                                    'newpassword': (UserWarning, 'string')})
def user_password_modify(handler, *args, **kwargs):
    """密码验证后修改密码
    """
    mobile = handler.json_args.get("mobile")
    code = handler.json_args.get("code")
    checksum = handler.json_args.get("checksum")
    oldpassword =  handler.json_args.get("oldpassword")
    newpassword =  handler.json_args.get("newpassword")
    status = UserBean().user_password_modify(mobile, code, checksum, oldpassword, newpassword)
    return handler.ok({"status": status})

@ews.route_sync_func('/user/verifycode/code', kwargs={})
def user_verify_code(handler):
    json_args = handler.json_args
    deviceid = json_args.get("mbimei", "")

    rds = db_pool.get_redis('main')
    key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=deviceid)

    login_times = rds.get(key)
    iscode = "0"
    if login_times and int(login_times) > 4:
        iscode = "1"

    ret = {
        "vcode_img_url": get_img_url(deviceid),
        "iscode": iscode
    }
    return handler.ok(ret)

@ews.route_sync_func('/user/verifycode/img', kwargs={})
def user_verify_code_img(handler):
    """图片验证码
    """
    json_args = handler.json_args
    deviceid = json_args.get("deviceid", "")
    vtype = json_args.get("vtype", define.VTYPE_LOGIN)
    redis_opt = db_pool.get_redis("main")
    code = ""
    for i in range(4):
        code += chr(random.randrange(ord('a'), ord('z') + 1))

    rds_name = rediskey.CRAZY_VERIFY_CODE_PREFIX.format(vtype=vtype, vkey=deviceid)
    redis_opt.set(rds_name, code, ex=5 * 60)
    handler.set_header('Content-Type', 'image/png')
    out = get_img(code)
    return handler.ok(out, extd="verifycode")


@ews.route_sync_func('/login/id2ck', kwargs={})
def uid2ck(handler, *args, **kwargs):
    uid = handler.json_args.get('uid', '')
    ck = ''
    if uid:
        ck = session.get_ck_by_uid(uid)
    if not ck:
        ck = session.make_ck(uid)
        session.set_ck_to_redis(ck, uid)
    return handler.ok({'ck': ck, 'uid': uid})

@ews.route_sync_func('/user/realname_auth', kwargs={})
def true_name_identify(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    realname = handler.json_args.get("realname", "")
    idcard = handler.json_args.get("idcard", "")
    uid = session.get_by_ck(ck).get('uid')
    code = handler.json_args.get("code")
    params = {
        "uid": uid,
        "realname": realname,
        "idcard": idcard,
        "code": code

    }
    UserBean().realname_auth(params)

    return handler.ok({})

@ews.route_sync_func('/user/bind_bank_card', kwargs={})
def user_bind_bank_card(handler, *args, **kwargs):
    ck = handler.json_args.get("ck")
    uid = session.get_by_ck(ck).get('uid')
    cardno = handler.json_args.get("cardno")

    params = {
        "uid": uid,
        "cardno": cardno
    }

    UserBean().bankcardverify(params)
    return handler.ok({})
