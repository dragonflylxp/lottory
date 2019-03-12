#encoding=utf-8
from User.userinfo import UserInfo
import traceback
from common.json_format import rpc_dumps
"""收集业务类方法作为RPC总入口
"""
class Interfaces(object):
    def login(self, params):
        """
        用户登录
        :param params:
        :return:
        """
        mobile = params.get("mobile")
        password = params.get("password")
        logintype = params.get("logintype")
        return UserInfo().Login(mobile)

    def user_info(self, params):
        """
        用户信息
        :param params:
        :return:
        """
        uid = params.get("uid")
        ret = UserInfo().userinfo(uid)
        return rpc_dumps(ret)

    def user_info_by_mobile(self, params):
        """

        :return:
        """
        mobile = params.get("mobile")
        return UserInfo().userinfo_by_mobile(mobile)

    def mobile_reg(self, params):
        """
        手机号注册
        :param params:
        :return:
        """
        return UserInfo().mobile_reg(params)

    def realname_auth(self, params):
        """
        实名认证
        :param params:
        :return:
        """
        return UserInfo().realname_auth(params)

    def password_reset(self, params):
        return UserInfo().password_reset(params)

    def password_modify(self, params):
        return UserInfo().password_modify(params)

    def bind_bankcard(self, params):
        return UserInfo().bind_bankcard(params)

    def login_log(self, params):
        return UserInfo().login_log(params)

    def userinfo_by_uids(self, params):
        uids = params.get("uids")
        return UserInfo().userinfo_by_uids(uids)


