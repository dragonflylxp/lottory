# coding: utf-8

import ujson
import random
import hashlib

import ews
from dbpool import db_pool
from util.tools import Log, detailtrace

logger = Log().getLog()

CK_PREFIX = 'nncp.session/ck/'
CK_TTL = 60 * 100

MC_PREFIX_UID = 'nncp:session:uid'
MC_PREFIX_CK = 'nncp:session:ck'
MC_UT_PREFIX = 'usertype'

DATA_TOKEN_PREFIX = 'crazybet.session/dt/'
DATA_TOKEN_TTL = 60 * 60 * 24 * 1


def random_key(length=16):
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    str = ''
    ub = len(chars) - 1
    for i in range(length):
        str += chars[random.Random().randint(0, ub)]
    return str


def make_ck(uid):
    rndkey = random_key()
    return (str(uid) + hashlib.md5(rndkey).hexdigest()).encode('base64')[:-1]


def get_ck_by_uid(uid):
    mc = db_pool.get_redis('session')
    return mc.get(MC_PREFIX_CK + str(uid))


def get_by_ck(ck, ss_err=True):
    """通过ck获取session信息
    @param ck: 通过登录得到的ck串
    @return: session内容，dict类型
    """
    mc = db_pool.get_redis('session')
    try:
        uid = mc.get(MC_PREFIX_UID + str(ck))
        if uid:
            # 校验当前用户是否在其他设备多点登录
            uid_ck = mc.get(MC_PREFIX_CK + str(uid))
            if ck != uid_ck:
                logger.debug('uid=%s^^^^^^ck=%s^^^^^uid_ck=%s', uid, ck, uid_ck)
                mc.delete(MC_PREFIX_UID + str(ck))
                raise ews.EwsError(ews.STATUS_MULTI_LOGIN_ERR)

            # 刷新ck有效期并返回
            set_ck_to_redis(ck, uid, refresh=True)
            return {
                'ck': ck,
                'uid': uid,
                'usertype': mc.get(MC_UT_PREFIX + str(ck)),
            }
        if ss_err:
            logger.debug(detailtrace("DetailTrace:{}".format(ck)))
            raise ews.EwsError(ews.STATUS_SESSION_ERR)
        else:
            return None
    finally:
        pass


def set_ck_to_redis(ck, uid, ttl=7 * 24 * 60 * 60, refresh=False):
    """设置memcached值
    """
    if not ck or not uid:
        raise ews.EwsError(ews.STATUS_SESSION_ERR)

    uid_key = MC_PREFIX_UID + str(ck)
    ck_key = MC_PREFIX_CK + str(uid)
    logger.debug('uid=%s^^^^^^ck=%s^^^^^uid_key=%s^^^^^^^^ck_key=%s', uid, ck, uid_key, ck_key)
    mc = db_pool.get_redis('session')
    try:
        mc.setex(uid_key, uid, ttl)
        mc.setex(ck_key, ck, ttl)
    except:
        raise ews.EwsError(ews.STATUS_SESSION_ERR)
    finally:
        pass


def del_ck_from_redis(ck):
    """从redis删除ck
    """
    if not ck:
        raise ews.EwsError(ews.STATUS_SESSION_ERR)

    uid_key = MC_PREFIX_UID + str(ck)
    mc = db_pool.get_redis('session')
    try:
        mc.delete(uid_key)
    except:
        raise ews.EwsError(ews.STATUS_SESSION_ERR)
    finally:
        pass


def apply_data_token(dt_type):
    """申请一个data_token
    """
    rds = db_pool.get_redis('main')
    for i in range(4):
        dt_key = hashlib.md5(str(random.random())).hexdigest()
        dt_secret = hashlib.md5(str(random.random())).hexdigest()
        if rds.setnx(DATA_TOKEN_PREFIX + dt_key, dt_secret) <= 0:
            continue
        rds.expire(DATA_TOKEN_PREFIX + dt_key, DATA_TOKEN_TTL)
        return {
            'key': dt_key,
            'secret': dt_secret,
            'ttl': DATA_TOKEN_TTL,
            'type': dt_type,
        }
    else:
        raise ews.EwsError(ews.STATUS_STATUS_BUSY)


def get_data_token(dt_key):
    """获取data_token
    """
    rds = db_pool.get_redis('main')
    return rds.get(DATA_TOKEN_PREFIX + dt_key)
