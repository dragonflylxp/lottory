#encoding=utf-8

import inspect
import MySQLdb
import traceback
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from common.dbs import BaseModel, access

logger = Log().getLog()


class UserInfoLogic(BaseModel):

    @access("r")
    def login(self, mobile):
        """
        获取用户登录信息
        :param mobile:
        :return:
        """
        sql =""" SELECT f_uid, f_username, f_loginpwd, f_islogin, f_photo, f_nickname, f_mobile, f_realname, f_idcard
            FROM t_user_info
            WHERE  f_mobile = %s LIMIT 1
        """
        ret = {}
        try:
            self.cursor.execute(sql, (mobile, ))
            ret = self.cursor.fetchone() or {}
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        return ret


    @access("r")
    def user_baseinfo(self, uid):
        """
        获取用户基础信息
        :param uid:
        :return:
        """
        sql = """
              SELECT f_uid uid, f_username username, f_photo photo, f_realname realname, f_idcard idcard, f_crtime crtime, f_mobile mobile
              FROM t_user_info
              WHERE  f_uid = %s LIMIT 1
        """

        bind_card = """
            SELECT f_cardno cardno, f_bank_main bankname
            FROM t_user_bankcard
            WHERE f_uid =%s
        """
        ret = {}
        try:
            self.cursor.execute(sql, (uid,))
            ret = self.cursor.fetchone() or {}

            self.cursor.execute(bind_card, (uid,))
            bank_info = self.cursor.fetchone() or {}
            ret.update({
                "cardno": bank_info.get("cardno", ""),
                "bankname": bank_info.get("bankname", "")
            })
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        return ret

    @access("r")
    def userinfo_by_mobile(self, mobile):
        """
        获取用户登录信息
        :param mobile:
        :return:
        """
        sql = """ SELECT f_uid, f_username, f_loginpwd, f_islogin, f_photo, f_nickname, f_mobile
                FROM t_user_info
                WHERE  f_mobile = %s LIMIT 1
            """
        ret = {}
        try:
            self.cursor.execute(sql, (mobile,))
            ret = self.cursor.fetchone() or {}
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        return ret


    @access("w")
    def user_reg(self, params):
        """
        获取用户登录信息
        :param mobile:
        :return:
        """

        username = params.get("username", "")
        nickname = params.get("nickname", "")
        loginpwd = params.get("password", "")
        tradepwd = params.get("password", "")
        mobile = params.get("mobile", "")
        is_login = params.get("is_login", "")
        photo = params.get("photo", "")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")
        ip = params.get("ip", "")

        #用户名为空时，默认为手机号
        if not username:
            username = mobile

        insert_user_sql = """
            INSERT INTO t_user_info
            (
                f_username,
                f_nickname,
                f_loginpwd,
                f_tradepwd,
                f_mobile,
                f_islogin,
                f_photo,
                f_subchannel,
                f_channel,
                f_platform
            )
            VALUES(
              %s, %s, %s, %s, %s, %s,%s, %s, %s, %s
            );
        """

        insert_account_info = """
            INSERT INTO t_account_info
            (f_uid)
            VALUES
            (%s);
        """

        try:
            self.cursor.execute(insert_user_sql, (username, nickname, loginpwd, tradepwd, mobile, is_login, photo, subchannel, channel, platform))
            uid = self.cursor.lastrowid
            self.cursor.execute(insert_account_info, (uid, ))
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise
        return uid

    @access("w")
    def realname_auth(self, uid, realname, idcard):

        sql = """
            UPDATE t_user_info
            SET f_realname = %s, f_idcard =%s
            WHERE f_uid=%s
        """
        status = 0
        try:
            status = self.cursor.execute(sql, (realname, idcard, uid))
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        return status

    @access("w")
    def password_reset(self, mobile, password):
        status = 1
        try:
            sql = """
                UPDATE t_user_info
                SET f_loginpwd=%s
                WHERE f_mobile=%s
            """
            self.cursor.execute(sql, (password, mobile))
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        return status

    @access("w")
    def password_modify(self, mobile, oldpassword, newpassword):
        sql = """
            UPDATE t_user_info
            SET f_loginpwd= %s
            WHERE f_mobile=%s AND f_loginpwd=%s
        """
        status = 0
        try:
            status = self.cursor.execute(sql, (newpassword, mobile, oldpassword))
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        return status

    @access("w")
    def bind_bankcard(self, uid, cardno, bank_main, bank_sub):
        sql = """
           INSERT INTO t_user_bankcard
            (
                f_uid,
                f_cardno,
                f_bank_main,
                f_bank_sub
            )
            VALUES
            (%s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE f_cardno= %s, f_bank_main=%s, f_bank_sub=%s
        """
        status = 0
        try:
            status = self.cursor.execute(sql, (uid, cardno, bank_main, bank_sub, cardno, bank_main, bank_sub))
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        return status

    @access("w")
    def login_log(self, params):
        """
        插入用户登录日志信息
        :param mobile:
        :return:
        """
        uid = params.get("uid", "")
        ip = params.get("ip", "")
        ua = params.get("ua", "")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")
        sql = """
            INSERT INTO t_user_login
            (
               f_uid,
               f_ip,
               f_ua,
               f_platform,
               f_channel,
               f_subchannel
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """
        ret = {}
        try:
            self.cursor.execute(sql, (uid, ip, ua, platform, channel, subchannel))
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
        finally:
            return ret

    @access("r")
    def userinfo_by_uids(self, uids):
        """
        获取用户登录信息
        :param mobile:
        :return:
        """
        sql = """ SELECT f_uid, f_username, f_loginpwd, f_islogin, f_photo, f_nickname, f_mobile
                    FROM t_user_info
                    WHERE  f_uid in %s
                """
        ret = {}
        try:
            self.cursor.execute(sql, (tuple(uids),))
            ret = self.cursor.fetchall() or []
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        return ret
