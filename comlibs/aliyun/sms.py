# -*- coding: utf-8 -*-
import sys
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid
from aliyunsdkcore.profile import region_provider

reload(sys)
sys.setdefaultencoding('utf8')

# # 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
#
# # ACCESS_KEY_ID/ACCESS_KEY_SECRET 根据实际申请的账号信息进行替换
ACCESS_KEY_ID = ""
ACCESS_KEY_SECRET = ""

# acs_client = None
def set_up(config):
    if config:
        return
    # sms = config.get("sms", {})
    # access_id = sms.get("access_id")
    # access_key = sms.get("access_key")
    # product_name = sms.get("product_name")
    # region = sms.get("region")
    # domain = sms.get("domain")
    # global acs_client
    # acs_client = AcsClient(access_id, access_key, region)
    # region_provider.add_endpoint(product_name, region, domain)

def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name);

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
    region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse


def query_send_detail(biz_id, phone_number, page_size, current_page, send_date):
    queryRequest = QuerySendDetailsRequest.QuerySendDetailsRequest()
    # 查询的手机号码
    queryRequest.set_PhoneNumber(phone_number)
    # 可选 - 流水号
    queryRequest.set_BizId(biz_id)
    # 必填 - 发送日期 支持30天内记录查询，格式yyyyMMdd
    queryRequest.set_SendDate(send_date)
    # 必填-当前页码从1开始计数
    queryRequest.set_CurrentPage(current_page)
    # 必填-页大小
    queryRequest.set_PageSize(page_size)

    # 调用短信记录查询接口，返回json
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
    region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    queryResponse = acs_client.do_action_with_exception(queryRequest)

    # TODO 业务处理

    return queryResponse


if __name__ == "__main__":
    __business_id = uuid.uuid1()
    __business_id = uuid.uuid1()
    print __business_id
    params = "{\"code\":\"12345\"}"
    print send_sms(__business_id, "13319403331", "阿里云短信测试专用", "SMS_127035066", params)
