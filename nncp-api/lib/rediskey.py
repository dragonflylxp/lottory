#!/usr/bin/env python
# encoding: utf-8

"""

redis数据库表定义，规则如下
前缀:类型:位置:关键字:参数占位




类型:
    KV ---> r.set(...), r.get( ...)
    HX ---> r.hset( ...), r.hget( ..)
    QUE ---> r.rpush( ...), r. lrange( ... )
    PUB ---- r.publish( ...), r.subscribe( ...)


参数占位:
    根据需要填充该项，如无则不填写。

Example:
    SERVER_MODULE_FILE_FUNC_TYPE
    CBET_JOBS_CHAMPIONJOB_SUPPORT_RATE_KV = "cbet:jobs:championjob:support:rate"
"""


REDIS_MOBILE_LOGIN_COUNT_LIMIT = "nncp:mobile:login:count:limit:{deviceid}"  # 手机登录限制
REDIS_USER_MOBILE_SEND_SMS_TIME_LIMIT = "nncp:user:mobile:sendsms:time:limit:{mobile}:{vtype}"  # 手机发送验证码时间限制
REDIS_USER_MOBILE_SEND_SMS_COUNT_LIMIT = "nncp:user:mobile:sendsms:count:limit:{tday}:{mobile}"  # 手机发送验证码次数限制
REDIS_USER_MOBILE_SMS_CODE = "nncp:user:mobile:sms:code:{mobile}"  # 手机验证码
REDIS_USER_MODFIY_PASSWORD_SIGN = "nncp:user:modify:password:sign:{mobile}"  #
# REDIS_USER_MODFIY_USERNAME_LIMIT = "nncp:user:modfiy:username:limit:{dmonth}:{uid}"
REDIS_MOBILE_REG_COUNT_LIMIT = "nncp:mobile:login:count:limit:{deviceid}" #手机注册限制
REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT = "nncp:user:mobile:sms:code:verify:limit:{mobile}"  # 验证参数
CRAZY_VERIFY_CODE_PREFIX = "nncp:user:verifycode:{vtype}:{vkey}"
REDIS_OPENCODE_EXPECT = "nncp:opencode:expect:{}"

REDIS_FOLLOW_WHEEL_INFO = "nncp:follow:wheel:info" #跟单轮播信息
REDIS_SELLER_HISTORY_GAINS = "nncp:seller:history:gains:{uid}"
REDIS_FOLLOW_PROJ_TOP_FIVE = "nncp:follow:proj:top5:{fid}"