# coding: utf-8
import hashlib
import hmac
import os
import base64
import json
import random
import time

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS
from Crypto.Cipher import PKCS1_v1_5 as PKCS5
from Crypto.Hash import MD5 as HASH
from Crypto.Cipher import ARC4 as RC4
from Crypto.Cipher import AES
import ujson
import urllib, urllib2
from util.tools import Log
import binascii

global logger
import requests
from binascii import b2a_hex, a2b_hex
import ews
logger = Log().getLog()

SECRECT_KEY = 'jd84*#g9'

esun_signer = None  # esun->lianlian 的加密签名器对象
lian_signer = None  # lianlian->esun 的加密签名器对象
partner_num = None  # 在连连支付的合作商户编号
partner_num_web = None
notify_url = None  # 连连支付的支付结果后台异步通知回调地址
notify_url_web = None  # 连连支付的支付结果后台异步通知回调地址-订单
withdraw_url = None
withdraw_notify_url = None
cipher = None
bankcardquery_url = None  # 查询银行卡地址
sign_skip_keys = {  # 不参与签名的字段
    'acct_name': '银行账号姓名',
    'bank_code': '银行编号',
    'card_no': '银行卡号',
    'flag_modify': '修改标记',
    'force_bank': '是否强制使用该银行的银行卡',
    'id_no': '证件号码',
    'id_type': '证件类型',
    'no_agree': '签约协议',
    'pay_type': '支付方式',
    'sign': '加密签名',
    'user_id': '用户编号',
}
verf_skip_keys = {  # 不参与签名的字段
    'sign': '加密签名',
}
bank_codes = {
    '01020000': '中国工商银行',
    '01030000': '中国农业银行',
    '01040000': '中国银行',
    '01050000': '中国建设银行',
    '03010000': '中国交通银行',
    '01000000': '邮储银行',
    '03020000': '中信银行',
    '03030000': '光大银行',
    '03040000': '华夏银行',
    '03050000': '民生银行',
    '03060000': '广东发展银行',
    '03080000': '招商银行',
    '03090000': '兴业银行',
    '03070000': '平安银行',
    '03100000': '浦发银行',
    '04031000': '北京银行',
    '04403600': '徽商银行',
    '05083000': '江苏银行',
    '04263380': '金华银行',
    '04243010': '南京银行',
    '04083320': '宁波银行',
    '04012900': '上海银行',
    '04123330': '温州银行',
}

aes = None


def set_up(confs):
    global cipher, aes, esun_signer, lian_signer, partner_num, notify_url, bankcardquery_url, notify_url_web, partner_num_web, withdraw_url, withdraw_notify_url
    dpath = os.path.dirname(__file__)
    with open(os.path.join(dpath, 'llpay_public_key.pem')) as f:
        lian_pub_key = RSA.importKey(f.read())
        lian_signer = PKCS.new(lian_pub_key)
        cipher = PKCS5.new(lian_pub_key)

    with open(os.path.join(dpath, 'llpay_private_nncp.pem')) as f:
        esun_pri_key = RSA.importKey(f.read())
        esun_signer = PKCS.new(esun_pri_key)

    partner_num = confs.get('partner_num')
    partner_num_web = confs.get("partner_num_web")
    notify_url = confs.get('notify_url')
    notify_url_web = confs.get("notify_url_web")
    bankcardquery_url = confs.get("bankcardquery_url")
    withdraw_url = confs.get("withdraw_url")
    withdraw_notify_url = confs.get("withdraw_notify_url")


def to_content(data, skip_keys):
    if isinstance(data, dict):
        ks = data.keys()
        ks.sort()
        content = '&'.join([i + '=' + str(data[i])
                            for i in ks
                            if data[i] and (i not in skip_keys)])
    else:
        content = data
    if isinstance(content, unicode):
        content = content.encode('utf-8')
    return content


def esun_sign_wap(data):
    content = to_content(data, {})
    h = HASH.new(content)
    # print "========== sign wap lianlian =========="
    # print content
    logger.debug("====lianlian wap sign content ====\n%s", content)
    sgn = esun_signer.sign(h)
    return base64.b64encode(sgn)


def esun_sign(data):
    content = to_content(data, sign_skip_keys)
    # print "content====", content
    h = HASH.new(content)
    # print content
    logger.debug("====lianlian sdk sign content ====\n%s", content)
    sgn = esun_signer.sign(h)
    return base64.b64encode(sgn)


def lian_verify(data, sgn):
    content = to_content(data, verf_skip_keys)
    h = HASH.new(content)
    sgn = base64.decodestring(sgn)
    return lian_signer.verify(h, sgn)


def encode_string(content):
    rc = RC4.new(SECRECT_KEY)
    data = rc.encrypt(str(content))
    return base64.urlsafe_b64encode(data).rstrip('=')


def decode_string(content):
    rc = RC4.new(SECRECT_KEY)
    data = base64.urlsafe_b64decode(str(content) + '==')
    return rc.decrypt(data)


def bank_card_test(card_no):
    """
    银行卡检查
    """
    url = bankcardquery_url
    params = {
        "oid_partner": partner_num,
        "sign_type": "RSA",
        "card_no": card_no
    }
    content = to_content(params, {})
    h = HASH.new(content)
    sgn = esun_signer.sign(h)
    sign = base64.b64encode(sgn)
    params["sign"] = sign

    f = None
    ret = dict()
    try:
        req = urllib2.Request(url, ujson.dumps(params))
        f = urllib2.urlopen(req, timeout=10)
        resp = f.read()
        logger.info("bank_card_test|resp=%s|%s", resp.encode("gbk"), resp)
        ret.update(ujson.loads(resp))
    finally:
        if f:
            f.close()

    return ret


def lianlian_make_risk_item(user_id, reg_time, truename, id_no, bind_mobile):
    """连连的风控参数
        frms_ware_categor： 商品类目，彩票默认 1007
        user_info_mercht_userno： 商户用户唯一标识 user_id
        user_info_dt_register: 注册时间
        user_info_identify_state： 是否实名认证
        user_info_full_name： 用户注册姓名
        user_info_id_type：用户注册证件类型
        user_info_id_no： 注册证件号
    """
    risk_item = {
        "frms_ware_category": "1007",
        "user_info_mercht_userno": user_id,
        "user_info_dt_register": reg_time,
        "user_info_identify_state": "1",
        "user_info_full_name": truename,
        "user_info_id_type": "0",
        "user_info_id_no": id_no,
        "user_info_identify_type": "3",
        "user_info_bind_phone": bind_mobile,
        # "goods_name": "xxxx",
        # "yyf_ware_category": ""
    }

    return risk_item


def to_format_datatime(r_datetime):
    strp_datetime = time.strptime(r_datetime, "%Y-%m-%d %H:%M:%S")
    ret_datatime = time.strftime("%Y%m%d%H%M%S", strp_datetime)
    return ret_datatime


def withdraw(oid, money, card_no, acct_name):
    data = {
        'oid_partner': partner_num_web,
        'api_version': '1.0',
        'no_order': oid,
        'dt_order': time.strftime('%Y%m%d%H%M%S'),
        'money_order': round(float(money), 2),
        'card_no': card_no,
        'acct_name': acct_name,
        'info_order': '提款',
        'flag_card': '0',
        'notify_url': withdraw_notify_url,
        'memo': 'nncp',
        'sign_type': 'RSA'
    }

    data['sign'] = esun_sign_wap(data)
    data = ujson.dumps(data)

    logger.info(data)
    decrypt_url = "https://www.niuniucaip.com/lianlian/encrypt/"
    plaintext = {
        "plaintext": data
    }

    r = requests.post(decrypt_url, data=ujson.dumps(plaintext))
    if r.status_code != 200:
        raise

    params = {
        "oid_partner": partner_num_web,
        "pay_load": r.content
    }

    print params
    # r = requests.post(withdraw_url, data=ujson.dumps(params), verify=False)

    headers = {'content-type': 'application/json'}
    r = requests.post(withdraw_url, data=ujson.dumps(params), headers=headers, verify=False)
    logger.info("r.content %s", r.content)

    if r.status_code != 200:
        return False
    else:
        resp = ujson.loads(r.content)

        ret_code = resp.get("ret_code")
        if ret_code == "0000":
            no_order = resp.get("no_order")
            return True
        else:
            return False


def query_withdraw_order(oid):
    url = "https://instantpay.lianlianpay.com/paymentapi/queryPayment.htm"

    data = {
        'oid_partner': partner_num_web,
        'api_version': '1.0',
        'no_order': oid,
        'sign_type': 'RSA'
    }
    data['sign'] = esun_sign_wap(data)
    data = ujson.dumps(data)
    headers = {'content-type': 'application/json'}

    r = requests.post(url, data=data, headers=headers)
    if r.status_code != 200:
        return {}
    else:
        resp = ujson.loads(r.content)
        return resp


def rsa_long_encrypt(msg, length=100):
    """
    单次加密串的长度最大为 (key_size/8)-11
    1024bit的证书用100， 2048bit的证书用 200
    """
    res = []
    for i in range(0, len(msg), length):
        res.append(cipher.encrypt(msg[i:i + length]))
    return "".join(res)

def get_cardbind_list(uid):
    url = "https://queryapi.lianlianpay.com/bankcardbindlist.htm"

    params = {
        'oid_partner': partner_num_web,
        'user_id': uid,
        'sign_type': 'RSA',
        'offset': '0'
    }
    content = to_content(params, {})

    h = HASH.new(content)
    sgn = esun_signer.sign(h)
    sign = base64.b64encode(sgn)
    params["sign"] = sign

    params = ujson.dumps(params)
    headers = {'content-type': 'application/json'}
    logger.info(content)
    r = requests.post(url, data=params, headers=headers)
    if r.status_code == 200:
        resp = ujson.loads(r.content)
        logger.info("get_cardbind_list %s", resp)
        ret_code = resp.get("ret_code")
        if ret_code == "0000":

            bank_list = resp.get("agreement_list")

            return bank_list
        elif ret_code in ["3007", "8901"]:
            return []
    raise ews.EwsError(ews.STATUS_RECHARGE_SEARCH_FAIL)

