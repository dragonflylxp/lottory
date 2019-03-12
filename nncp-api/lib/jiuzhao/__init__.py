# coding=utf-8

import os
import datetime
import urllib
import base64
import copy
import re
import traceback
import hashlib
import ujson
import requests
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS
from Crypto.Cipher import PKCS1_v1_5 as PKCS5
from util.tools import Log
import time
import collections
import urllib
from wechat.Monitor import send_textcard_message

logger = Log().getLog()

configs = {}
wap_configs = dict()
pri_key = None
pub_key = None
cipher = None
def set_up(confs):
    global signer, verifier, cipher
    dpath = os.path.dirname(__file__)
    pri_pem = os.path.join(dpath, "rsa_private_key.pem")
    pub_pem = os.path.join(dpath, "rsa_public_key.pem")
    with open(pri_pem) as f:
        pri_key = RSA.importKey(f.read())
        signer = PKCS.new(pri_key)


    with open(pub_pem) as f:
        pub_key = RSA.importKey(f.read())
        verifier = PKCS.new(pub_key)
        cipher = PKCS5.new(pub_key)

    configs.update(confs)
    wap_configs.update(configs.get("wap"))


def jz_sign(content):
    """RSA 私钥生成签名
    """
    h = SHA.new(content)
    signature = signer.sign(h)
    sign = base64.b64encode(signature)
    return sign


def to_content_by_key(data):
    """签名内容串对阵顺序
    """
    sorted_key = ["notifyUrl", "outTradeNo", "returnUrl", "subject", "terminalIp", "totalAmount", "tradeType"]

    if isinstance(data, dict):
        content = "&".join([x + '=' + str(data[x]) + '' for x in sorted_key if data.get(x)])

    else:
        content = data

    return content


def to_content(data, filter_keys=[]):
    """签名内容串
    """
    if not filter_keys: filter_keys = []

    if isinstance(data, dict):
        sp = sorted(data.items())
        content = "&".join([str(i[0]) + '=' + str(i[1] + '') for i in sp if i[0] not in filter_keys and i[1]])
    else:
        content = data

    if isinstance(content, unicode):
        content = content.encode('utf-8')

    return content


def build_unifiedorder(params):
    """创建统一订单参数
    """
    ip = params.get("ip")
    sign_params = {
        "notifyUrl": wap_configs.get("notifyUrl", ""),
        "outTradeNo": str(params.get("oid", "")),
        "returnUrl": wap_configs.get("returnUrl", ""),
        "subject": "xxxx",
        "terminalIp": params.get("ip", ""),
        "totalAmount": int(float(params.get("money", "")) * 100),
        "tradeType": params.get("tradeType", "H5")
    }
    logger.info(sign_params)
    req_params = to_content_by_key(sign_params)

    cipher_text = base64.b64encode(cipher.encrypt(req_params))
    logger.info(cipher_text)

    signStr = "data=" + cipher_text + "&merchantId=" + wap_configs.get("merchantId", "")

    sign = jz_sign(str(signStr))

    url = "https://gw.rrzsports.com/tradePay"
    post_params = {
        "merchantId": wap_configs.get("merchantId", ""),
        "sign": sign,
        "data": cipher_text
    }

    r = requests.post(url, data=post_params, verify=False)
    logger.info(r.content)
    if r.status_code == 200:
        resp = ujson.loads(r.content)
        code = resp.get("code")
        if code == "0":
            path = resp.get("resp")
            return path
        else:
            raise
    else:
        raise #todo
    return


def get_jz_trade_req(params):
    """获取签名后的请求串
    """

    seq = to_content_by_key(params)
    sign = jz_sign(seq)
    s = seq + '&sign="' + urllib.quote(sign) + '"&merchantId="%s"' % wap_configs["merchantId"]
    return s



def jz_verify(args):
    """签名验证
    """

    params = copy.copy(args)
    sign = params.pop("sign")
    seq = to_content(params, ["sign", "sign_type"])
    logger.info("verify |seq=%s|sign=%s", seq, sign)
    sign = base64.b64decode(sign)
    h = SHA.new(seq)
    return True == verifier.verify(h, sign)


def join_dict(dic):
    return '&'.join('{}={}'.format(k, v) for k, v in sorted(dic.items()))
