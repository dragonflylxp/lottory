# coding:utf-8

import requests
import ujson
from dbpool import db_pool
corpid = "*****"
corpsecret = "******"


def get_wechat_access_token():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(corpid=corpid,
                                                                                                        corpsecret=corpsecret)
    r = db_pool.get_redis("main")
    access_token = r.get("nncp:wechat:work:token")
    if not access_token:
        try:
            req = requests.get(url, verify=False)
        except:
            req = requests.get(url, verify=False)
        access_token = ujson.loads(req.content).get("access_token")
        r.set("nncp:wechat:work:token", access_token, 60*60)
        return access_token
    else:
        return access_token


def send_textcard_message(msgtype='test', servicename="", exceptinfo="",  more_url="http://127.0.0.1"):
    access_token = get_wechat_access_token()
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
        access_token=access_token)

    description = """
        <div class=\"gray\">消息类型：{}</div> 
        <div class=\"normal\">服务：{}</div> 
        <div class=\"highlight\">异常信息：{}</div>
    """.format(msgtype, servicename, exceptinfo)


    data = {
        "touser": "@all",
        "toparty": "@all",
        "totag": "@all",
        "msgtype": "textcard",
        "agentid": 1000003,
        "textcard": {
            "title": "告警通知",
            "description": description,
            "url": more_url,
            "btntxt": "更多"
        }
    }

    req = requests.post(url, verify=False, data=ujson.dumps(data))
    info = ujson.loads(req.content)
    print info

    errcode = info.get("errcode")

    if errcode != 0:
        #todo sms
        pass


if __name__ == "__main__":
    # get_wechat_access_token()
    # send_text_message()
    send_textcard_message()
