# encoding=utf-8

import inspect
import MySQLdb
import traceback
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from logic.User.userinfo import UserInfoLogic

logger = Log().getLog()


class UserInfo(object):
    def Login(self, login_mobile):
        """
            :param login_mobile: 登录手机号
            :param login_password: 登录密码
            :param login_type: 登录类型
            :return:
        """

        user_info = UserInfoLogic().login(login_mobile)
        return user_info

    def userinfo(self, uid):
        user_info = UserInfoLogic().user_baseinfo(uid)
        return user_info

    def userinfo_by_mobile(self, mobile):
        user_info = UserInfoLogic().userinfo_by_mobile(mobile)
        return user_info

    def mobile_reg(self, params):
        """
        手机注册
        :param params:
        :return:
        """
        username = params.get("username", "")
        nickname = params.get("nickname", "")
        loginpwd = params.get("password", "")
        tradepwd = params.get("password", "")
        mobile = params.get("mobile", "")
        is_login = params.get("is_login", "")
        photo = params.get("photo", "")
        channel = params.get("channel", "")

        params.update({"is_login": 1})

        uid = UserInfoLogic().user_reg(params)

        return uid

    def realname_auth(self, params):
        uid = params.get("uid")
        realname = params.get("realname")
        idcard = params.get("idcard")
        status = UserInfoLogic().realname_auth(uid, realname, idcard)
        return status

    def password_reset(self, params):
        mobile = params.get("mobile")
        password = params.get("password")
        status = UserInfoLogic().password_reset(mobile, password)
        return status

    def password_modify(self, params):
        mobile = params.get("mobile")
        oldpassword = params.get("oldpassword")
        newpassword = params.get("newpassword")
        status = UserInfoLogic().password_modify(mobile, oldpassword, newpassword)
        return status

    def bind_bankcard(self, params):
        # uid, cardno, bank_main, bank_sub
        uid = params.get("uid", "")
        cardno = params.get("cardno", "")
        bank_main = params.get("bank_main", "")
        bank_sub = params.get("bank_sub", "")

        status = UserInfoLogic().bind_bankcard(uid, cardno, bank_main, bank_sub)
        return status

    def login_log(self, params):
        """
            :param login_mobile: 登录手机号
            :param login_password: 登录密码
            :param login_type: 登录类型
            :return:
        """
        user_info = UserInfoLogic().login_log(params)
        return user_info

    def userinfo_by_uids(self, uids):
        user_info = UserInfoLogic().userinfo_by_uids(uids)
        return user_info
