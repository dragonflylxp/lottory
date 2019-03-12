# coding: utf-8
import string
import uuid
from random import sample

import datetime
import ews
import time

import requests
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import re
import define
import hashlib
import session
import ujson
from util.tools import Log
from dbpool import db_pool
from aliyun import sms
import rediskey
import lianlian

global logger
logger = Log().getLog()

PATTERN = '^0\d{2,3}\d{7,8}$|^1[345678l9]\d{9}$|^14\d{8}'
idcaed_prog = re.compile("^[1-9]\d{7}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}$|^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X|x)$")
class UserBean():

    def user_login(self, params):
        origin_params = params
        login_type = params.get("login_type", "mobile")
        mobile = params.get("mobile", "")
        password = params.get("password", "")
        verifycode = params.get("verifycode", "")
        deviceid = params.get("mbimei")

        rds = db_pool.get_redis('main')
        if login_type == define.DEFIND_USER_LOGIN_TYPE:
            if not re.match(PATTERN, mobile):
                # 手机号非法
                key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=deviceid)
                rds.incr(key, 1)
                raise ews.EwsError(ews.STATUS_USER_MOBILE_FORMAT_ERROR)
            login_password = hashlib.md5(password + define.DEFIND_LOGIN_SALT).hexdigest()

            verify = self.verify_img_code(verifycode, deviceid)
            if not verify:
                raise ews.EwsError(ews.STATUS_USER_IMG_CODE_ERROR)

            module = "user"
            method = "login"
            params = {"mobile": mobile, "password": password, "logintype": login_type}
            user_info = {}
            with get_rpc_conn(module) as proxy:
                user_info = proxy.call(method, params)

                if not user_info:
                    raise ews.EwsError(ews.STATUS_LOGIN_NOT_REG)
                    # 用户没有注册

                loginpwd = user_info.get("f_loginpwd")
                if login_password != loginpwd:
                    key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=deviceid)
                    rds.incr(key, 1)
                    raise ews.EwsError(ews.STATUS_USER_LOGIN_PASSWORD_ERROR)

                #todo 登录日志
                origin_params.update({"uid": user_info.get("f_uid")})
                proxy.call("login_log", origin_params)

                uid = user_info.get("f_uid")
                username = user_info.get("f_username")
                nickname = user_info.get("f_nickname")
                mobile = user_info.get("f_mobile")
                truename = user_info.get("f_truename")
                idcard = user_info.get("f_idcard")
                ck = session.make_ck(uid)
                session.set_ck_to_redis(ck, uid, ttl=24 * 60 * 60)

                module = "account"
                method = "user_account"
                params = {"uid": uid}
                user_account = {}
                with get_rpc_conn(module) as proxy:
                    try:
                        user_account = proxy.call(method, params)
                    except:
                        logger.error(traceback.format_exc())
                        raise ews.EwsError(ews.STATUS_LOGIN_FAIL)
                    user_account = ujson.loads(user_account)

                ret = {
                    "uid": uid,
                    "ck": ck,
                    "mobile": mobile,
                    "truename": truename,
                    "idcard": idcard,
                    "username": username,
                    "nickname": nickname
                }
                ret.update(user_account)
                key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=deviceid)
                rds.delete(key)
                return ret

        else:
            raise ews.EwsError(ews.STATUS_LOGIN_FAIL)

    def check_account(self, params):
        with get_rpc_conn("account") as proxy:
            payinfo = proxy.call("check_account", params)
            payinfo = ujson.loads(payinfo)
            paystatus = payinfo.get("paystatus")
            paymoney = payinfo.get("paymoney")
            if paystatus != define.ORDER_PAY_STATUS_SUCC:
                raise ews.EwsError(ews.STATUS_RPC_TRADE_ERROR, define.PAY_STATUS_REMARK[paystatus])
        return paymoney

    def user_account(self, params):
        module = "account"
        method = "user_account"

        user_account = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_account = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

            user_account = ujson.loads(user_account)
        return user_account

    def user_info(self, params):
        module = "account"
        method = "user_account"
        user_account = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_account = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)
            user_account = ujson.loads(user_account)

        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

        ret = {}
        ret.update(user_account)
        ret.update(user_info)

        return ret

    def user_account(self, params):
        module = "account"
        method = "user_account"

        user_account = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_account = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

            user_account = ujson.loads(user_account)
        return user_account

    def user_account_detail(self, params):
        module = "account"
        method = "user_account_detail"

        account_detail = {}
        with get_rpc_conn(module) as proxy:
            try:
                account_detail = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

            account_detail = ujson.loads(account_detail)


        details = account_detail.get("details", [])
        count = account_detail.get("count", 0)
        user_list = []

        #:"f_crtime":1520666344,"f_pid":57,"f_inout":1,"f_money":32.0,"f_id":23,"f_uptime":1520666344,"f_lotid":28,"f_uid":1,"f_balance":9648.0
        for detail in details:
            inout = int(detail.get("f_inout"))
            if inout == define.ACCOUNT_LOG_TYPE_PAID:
                continue
            user_list.append({
                "crtime": detail.get("f_crtime"),
                "pid": detail.get("f_oid"),
                "inout": detail.get("f_inout"),
                "money": detail.get("f_money"),
                "desc": define.ACCOUNT_LOG_DESC.get(inout),
                "id": detail.get("f_id"),
                "balance": float(detail.get("f_balance_recharge"))+float(detail.get("f_balance_draw")),
                "lotid": detail.get("f_lotid")
            })

        ret = {}
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        ret.update({
            "list": user_list,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno
        })

        return ret

    def get_user_info_by_mobile(self, mobile):
        module = "user"
        method = "user_info_by_mobile"

        params = {"mobile": mobile}
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)
            return user_info
        raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

    def user_password_modify(self, mobile, code, checksum, oldpassword, newpassword):
        if checksum != hashlib.md5(str(mobile) + str(code) + define.DEFIND_SMS_SALT).hexdigest():
            raise ews.EwsError(ews.STATUS_USER_MOBILE_VERIFY_ERROR)

        if oldpassword == newpassword:
            raise ews.EwsError(ews.STATUS_USER_PASSWORD_MODIFY_SAMEPWD)

        params = {
            "mobile": mobile,
            "oldpassword": hashlib.md5(oldpassword + define.DEFIND_LOGIN_SALT).hexdigest(),
            "newpassword": hashlib.md5(newpassword + define.DEFIND_LOGIN_SALT).hexdigest()
        }
        module = "user"
        method = "password_modify"
        with get_rpc_conn(module) as proxy:
            status = 0
            try:
                status = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_PASSWORD_MODIFY_FAIL)
            if status < 1:
                raise ews.EwsError(ews.STATUS_USER_LOGIN_PASSWORD_ERROR)
            return status
        raise ews.EwsError(ews.STATUS_USER_PASSWORD_MODIFY_FAIL)

    def user_password_reset(self, mobile, code, checksum, password):
        if checksum != hashlib.md5(str(mobile) + str(code) + define.DEFIND_SMS_SALT).hexdigest():
            raise ews.EwsError(ews.STATUS_USER_MOBILE_VERIFY_ERROR)
        password = hashlib.md5(password + define.DEFIND_LOGIN_SALT).hexdigest()

        params = {
            "mobile": mobile,
            "password": password
        }
        module = "user"
        method = "password_reset"
        with get_rpc_conn(module) as proxy:
            status = 0
            try:
                status = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_PASSWORD_RESET_FAIL)
            return status
        raise ews.EwsError(ews.STATUS_USER_PASSWORD_RESET_FAIL)


    def user_verify_sms(self, mobile, code):
        pt = re.compile('^0\d{2,3}\d{ 7,8}$|^1[3456789]\d{9}$|^147\d{8}')
        phonematch = pt.match(mobile)
        if not phonematch:
            raise ews.EwsError(ews.STATUS_USER_MOBILE_FORMAT_ERROR)

        if not code:
            raise ews.EwsError(ews.STATUS_USER_MOBILE_CODE_EMPTY)

        rds = db_pool.get_redis('main')
        _code = rds.get(rediskey.REDIS_USER_MOBILE_SMS_CODE.format(mobile=mobile)) or ""

        if not _code:
            raise ews.EwsError(ews.STATUS_USER_MOBILE_CODE_EXPIRE)

        if str(_code) != str(code):
            raise ews.EwsError(ews.STATUS_USER_MOBILE_CODE_ERROR)

        checksum = hashlib.md5(str(mobile) + str(code) + define.DEFIND_SMS_SALT).hexdigest()
        return {"checksum": checksum, "code": code, "mobile": mobile}


    def user_send_sms(self, mobile, vtype):
        """
        :param mobile:
        :param vtype:
        :return:
        """

        pt = re.compile('^0\d{2,3}\d{6,7,8}$|^1[3456789]\d{9}$|^147\d{8}')
        phonematch = pt.match(mobile)
        if not phonematch:
            raise ews.EwsError(ews.STATUS_USER_MOBILE_FORMAT_ERROR)
        #
        userinfo = self.get_user_info_by_mobile(mobile)
        if vtype == "reg":
            if userinfo:
                raise ews.EwsError(ews.STATUS_USER_MOBILE_ALREAD_REG)
        elif vtype == "auth":
            if not userinfo:
                raise ews.EwsError(ews.STATUS_USER_MOBILE_ACCOUNT_NOT_FOUND)
            if userinfo.get("realname"):
                raise ews.EwsError(ews.STATUS_ALREADY_TRUENAME)

        else:
            if not userinfo:
                raise ews.EwsError(ews.STATUS_USER_MOBILE_ACCOUNT_NOT_FOUND)

        rds = db_pool.get_redis('main')
        data = {}
        # 短信服务发送验证码(频率限制)
        time_limit_key = rediskey.REDIS_USER_MOBILE_SEND_SMS_TIME_LIMIT.format(
            mobile=mobile, vtype=vtype)
        timestamp = rds.get(time_limit_key)
        if timestamp:
            data['timeleft'] = 60 - (int(time.time()) - int(timestamp))
            return data

        tday = datetime.datetime.now().weekday()
        key = rediskey.REDIS_USER_MOBILE_SEND_SMS_COUNT_LIMIT.format(mobile=mobile, tday=tday)
        days_code = rds.get(key)
        # TODO  测试屏蔽

        if days_code:
            if int(days_code) >= 20:
                raise ews.EwsError(ews.STATUS_AUTH_MOBILE_CODE_MULNUM)

        # 发送验证码
        codelist = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        code = sample(codelist, 4)
        code = ''.join([str(i) for i in code])
        logger.info("mobile %s code:%s", vtype, code)

        params = {
            "code": code
        }
        SMS_TPL = {
            'reg': 'SMS_127035066',
            'pwd': 'SMS_127035065',
            'auth': 'SMS_127035069',
            'withdraw': 'SMS_133270931'
        }
        resp = sms.send_sms(uuid.uuid1(), mobile, "小牛", SMS_TPL.get(vtype, 'SMS_127035066'), ujson.dumps(params))
        resp = ujson.loads(resp)
        resp_code = resp.get("Code")

        if resp_code != "OK":
            logger.debug(resp)
            raise ews.EwsError(ews.STATUS_USER_SEND_SMS_FAIL)

        rds.setex(rediskey.REDIS_USER_MOBILE_SMS_CODE.format(mobile=mobile), code, 300)  # 验证码有效期5分钟
        rds.setex(time_limit_key, int(time.time()), 60)  # 频率限制1分钟

        rds.incr(key, 1)
        rds.expire(key, 24 * 60 * 60)

        data['lefttime'] = 60
        data['expired'] = 300
        return data

    def user_mobile_reg(self, params):

        password = params.get("password")
        password = hashlib.md5(password + define.DEFIND_LOGIN_SALT).hexdigest()
        mobile = params.get("mobile")
        idfa = params.get("idfa")
        code = params.get("code")

        rds = db_pool.get_redis("main")
        if not re.match(PATTERN, mobile):
            # 手机号非法
            key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=idfa)
            rds.incr(key, 1)
            raise ews.EwsError(ews.STATUS_USER_MOBILE_FORMAT_ERROR)

        params.update({"password": password})

        userinfo = self.get_user_info_by_mobile(mobile)
        if userinfo:
            raise ews.EwsError(ews.STATUS_USER_MOBILE_ALREAD_REG)
        else:
            _code = rds.get(rediskey.REDIS_USER_MOBILE_SMS_CODE.format(mobile=mobile))
            limit_count = rds.incr(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))
            rds.expire(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile), 6*60*60)
            if limit_count >= 6:
                logger.error('Mobile sms code verify limit! mobile=%s|count=%s|key=%s', mobile, limit_count,rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT)
                raise ews.EwsError(ews.STATUS_USER_VERIDFY_CODE_LIMIT_ERROR)
            if _code != code:
                raise ews.EwsError(ews.STATUS_USER_SMS_CODE_ERROR)

            #注册
            module = "user"
            method = "mobile_reg"
            uid = 0
            with get_rpc_conn(module) as proxy:
                try:
                    uid = proxy.call(method, params)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_USER_REG_FAIL)

                #登录日志
                params.update({"uid": uid})
                proxy.call("login_log", params)

            #写ck
            ck = session.make_ck(uid)
            session.set_ck_to_redis(ck, uid, ttl=7 * 24 * 60 * 60)
            rds.delete(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))

            return {"uid": uid, "ck": ck}

    def verify_img_code(self, verifycode, deviceid):
        """验证图片验证码

        """
        rds = db_pool.get_redis('main')
        key = rediskey.REDIS_MOBILE_LOGIN_COUNT_LIMIT.format(deviceid=deviceid)
        login_count = rds.get(key) or 0
        logger.info("verifycode:%s, deviceid:%s", verifycode, deviceid)
        if int(login_count) <= 4:
            return True

        rds_name = rediskey.CRAZY_VERIFY_CODE_PREFIX.format(vtype=define.VTYPE_LOGIN, vkey=deviceid)
        code = rds.get(rds_name)

        if code.lower() == verifycode.lower():
            return True
        return False

    def realname_auth(self, params):
        """
        实名认证
        :param params:
        :return:
        """
        idcard = params.get("idcard")
        truename = params.get("realname")
        code = params.get("code")
        rds = db_pool.get_redis("main")

        self.__check_auth_idcard(idcard, truename)
        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

        # 获取实名信息接口
        if user_info.get("realname", ""):
            # 实名认证
            raise ews.EwsError(ews.STATUS_ALREADY_TRUENAME)
        mobile = user_info.get("mobile")
        _code = rds.get(rediskey.REDIS_USER_MOBILE_SMS_CODE.format(mobile=mobile))
        limit_count = rds.incr(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))
        rds.expire(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile), 6 * 60 * 60)
        if limit_count >= 6:
            logger.error('Mobile sms code verify limit! mobile=%s|count=%s|key=%s', mobile, limit_count,rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT)
            raise ews.EwsError(ews.STATUS_USER_VERIDFY_CODE_LIMIT_ERROR)
        if _code != code:
            raise ews.EwsError(ews.STATUS_USER_SMS_CODE_ERROR)

        rds.delete(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))
        status = self.verifyIdcard(idcard, truename)

        if not status:
            raise ews.EwsError(ews.STATUS_AUTH_TRUENAME_FAIL)
        module = "user"
        method = "realname_auth"
        ret = {}
        with get_rpc_conn(module) as proxy:
            try:
                ret = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_AUTH_TRUENAME_FAIL)
        return

    def modify_password(self, params):
        module = "user"
        method = "modify_password"

        ret = {}
        with get_rpc_conn(module) as proxy:
            try:
                ret = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)
        return

    def __check_auth_idcard(self, idcard, truename):
        """
        检查身份证是否绑定
        :return:
        """

        check_idcard = idcaed_prog.match(idcard)
        check_char = string.digits + string.letters
        for char in truename:
            if char in check_char:
                raise ews.EwsError(ews.STATUS_AUTH_CHECK_TRUENAME)

        if not check_idcard:
            raise ews.EwsError(ews.STATUS_AUTH_CHECK_IDCARD)

        birthday = idcard[6:14]
        is_adult = self.check_is_adult(datetime.datetime.strptime(birthday, "%Y%m%d"))

        if is_adult == "0":
            raise ews.EwsError(ews.STATUS_NOT_ADULT)
        elif is_adult == "-1":
            raise ews.EwsError(ews.STATUS_AUTH_CHECK_IDCARD)


    def check_is_adult(self, birthday):
        """
        是否成年
        :param birthday: 19901012
        :return:
        """
        now = datetime.datetime.now()
        birth_year = now.year - birthday.year
        if birth_year < 0 or birth_year > 200:
            # 未满18
            return "-1"
        elif birth_year < 18:
            return "0"
        elif birth_year == 18:
            if now.month > birthday.month:
                return "0"
            elif now.month == birthday:
                if now.day - birthday.day:
                    return "0"

        return "1"

    def verifyIdcard(self, idcard, truename):
        url = "http://aliyunverifyidcard.haoservice.com/idcard/VerifyIdcardv2?cardNo={cardNo}&realName={realName}"

        url = url.format(cardNo=idcard, realName=truename)
        header = {
            'Authorization': 'APPCODE ' + "dc384ff70f79452dac4b3a7f5b107c5d"
        }
        r = requests.get(url, headers=header)
        logger.info(r.content)
        if r.status_code != 200:
            raise ews.EwsError(ews.STATUS_AUTH_TRUENAME_FAIL)
        resp = ujson.loads(r.content)

        error_code = resp.get("error_code")
        result = resp.get("result")
        isok = resp.get("isok")
        if error_code == 0:
            return True

        raise ews.EwsError(ews.STATUS_AUTH_NOT_MATCHING)

    def bankcardverify(self, params):

        cardno = params.get("cardno")
        bank_code_info = lianlian.bank_card_test(cardno)
        ret_code = bank_code_info.get("ret_code")
        if ret_code != "0000":
            raise ews.EwsError(ews.STATUS_BIND_CARD_FAIL)

        bank_code = bank_code_info.get("bank_code") if bank_code_info.get("bank_code") else ""
        bank_name = bank_code_info.get("bank_name") if bank_code_info.get("bank_name") else ""

        params.update({
            "bank_main": bank_name,
            "bank_sub": bank_code

        })
        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

        # 获取实名信息接口

        if user_info.get("cardno", ""):
            #已经绑定银行卡
            raise ews.EwsError(ews.STATUS_ALREADY_BIND_CARD)

        if not user_info.get("realname", ""):
            # 没有实名认证
            raise ews.EwsError(ews.STATUS_USER_NOT_AUTH)


        url = "http://jisubank2.market.alicloudapi.com/bankcardverify/verify?bankcard={bankcard}&realname={realname}"
        realname = user_info.get("realname", "")
        url = url.format(bankcard=cardno, realname=realname)
        header = {
            'Authorization': 'APPCODE ' + "dc384ff70f79452dac4b3a7f5b107c5d"
        }
        r = requests.get(url, headers=header)

        # {
        #     "status": "0",
        #     "msg": "ok",
        #     "result": {
        #         "bankcard": "6228480402564881235",
        #         "realname": "张先生",
        #         "verifystatus": "1",
        #         "verifymsg": "抱歉，银行卡号校验不一致！"
        #     }
        # }
        logger.info(r.content)
        if r.status_code != 200:
            raise ews.EwsError(ews.STATUS_BIND_CARD_FAIL)
        resp = ujson.loads(r.content)

        result = resp.get("result")
        status = resp.get("status")
        verifystatus = result.get("verifystatus")
        if status == "0":
            module = "user"
            method = "bind_bankcard"
            user_info = {}
            with get_rpc_conn(module) as proxy:
                try:
                    status = proxy.call(method, params)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)
                if not status:
                    raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)
            return True

        raise ews.EwsError(ews.STATUS_REALNAME_NOT_MATCHING_BANKCARD)
