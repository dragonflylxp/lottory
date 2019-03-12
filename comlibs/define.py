# encoding: utf-8

DEFIND_USER_LOGIN_TYPE = "mobile" #用户登录方式
DEFIND_LOGIN_SALT = "$nncp2018"

# 追号状态
CHASE_STATUS_FAILPAY    = -1 #追号支付失败
CHASE_STATUS_UNPAY      = 0  #追号未支付
CHASE_STATUS_SUCC       = 1  #追号进行中
CHASE_STATUS_PRIZESTOP  = 2  #追号中奖停止
CHASE_STATUS_FINISHSTOP = 3  #追号追完停止
CHASE_STATUS_CANCEL     = 4  #追号取消



# 订单状态
ORDER_STATUS_FAILPAY    = -1 #下单支付失败
ORDER_STATUS_UNPAY      = 0  #下单未支付
ORDER_STATUS_SUCC       = 1  #支付未出票
ORDER_STATUS_PRINT_PART = 2  #部分出票(部分撤单)
ORDER_STATUS_PRINT_ALL  = 3  #全部出票
ORDER_STATUS_CANCEL     = 4  #全部撤单

ORDER_JPRIZE_UNCAL      = 0  #未算奖
ORDER_JPRIZE_PRIZE      = 1  #已中奖
ORDER_JPRIZE_LOSE       = 2  #未中奖
ORDER_JPRIZE_PRIZED     = 3  #已派奖/已撤单退款

# 票状态
TICKET_STATUS_SAVED   = 0  # 已拆票
TICKET_STATUS_PRINTED = 1  # 已出票
TICKET_STATUS_PRIZED  = 2  # 已中奖
TICKET_STAUTS_LOSE    = 3  # 未中奖
TICKET_STATUS_CANCEL  = 4  # 已撤单

TICKET_JPRIZE_UNCAL   = 0  # 未算奖
TICKET_JPRIZE_PRIZE   = 1  # 算奖已中奖
TICKET_JPRIZE_LOSE    = 2  # 算奖未中奖
TICKET_JPRIZE_PRIZED  = 3  # 中奖已派奖


# 支付状态
ORDER_PAY_STATUS_FAILED           = -1 # 支付异常(其他原因)
ORDER_PAY_STATUS_SUCC             = 0  # 支付成功
ORDER_PAY_STATUS_ALREADY_PAID     = 1 # 订单已支付
ORDER_PAY_STATUS_COUPON_UNKNOWN   = 2 # 优惠券不存在
ORDER_PAY_STATUS_COUPON_EXPIRE    = 3 # 优惠券已过期
ORDER_PAY_STATUS_COUPON_USED      = 4 # 优惠券已使用
ORDER_PAY_STATUS_COUPON_ILLEGAL   = 5 # 优惠券不满足使用条件
ORDER_PAY_STATUS_NOTENOUGH_MONEY  = 6 # 余额不足
ORDER_PAY_STATUS_NOT_FREEZE       = 7 # 未冻结
ORDER_PAY_STATUS_FREEZE_ERROR     = 8 # 冻结账户异常
ORDER_PAY_STATUS_COUPON_NEGTIVE   = 9 # 优惠券未激活

PAY_STATUS_REMARK = {
    ORDER_PAY_STATUS_FAILED: "支付异常(其他原因)",
    ORDER_PAY_STATUS_SUCC: "支付成功",
    ORDER_PAY_STATUS_ALREADY_PAID: "订单已支付",
    ORDER_PAY_STATUS_COUPON_UNKNOWN: "优惠券不存在",
    ORDER_PAY_STATUS_COUPON_EXPIRE: "优惠券已过期",
    ORDER_PAY_STATUS_COUPON_NEGTIVE: "优惠券未激活",
    ORDER_PAY_STATUS_COUPON_USED: "优惠券已使用",
    ORDER_PAY_STATUS_COUPON_ILLEGAL: "优惠券不满足使用条件",
    ORDER_PAY_STATUS_NOTENOUGH_MONEY: "余额不足",
    ORDER_PAY_STATUS_NOT_FREEZE: "未冻结",
    ORDER_PAY_STATUS_FREEZE_ERROR: "冻结账户异常"
}

# 账户流水类型
ACCOUNT_LOG_TYPE_FREEZE = 1  # 下单冻结
ACCOUNT_LOG_TYPE_PAID   = 2  # 解冻扣款
ACCOUNT_LOG_TYPE_PRIZE  = 3  # 派奖
ACCOUNT_LOG_TYPE_CANCEL = 4  # 撤单
ACCOUNT_LOG_TYPE_RECHARGE = 5 # 充值
ACCOUNT_LOG_TYPE_WITHDRAW = 6 # 提款
ACCOUNT_LOG_TYPE_CHASEPAY = 7 # 追号扣款
ACCOUNT_LOG_TYPE_CHASECANCEL = 8 # 追号退款
ACCOUNT_LOG_TYPE_FOLLOWFEE_SUB = 9 # 跟单扣佣金
ACCOUNT_LOG_TYPE_FOLLOWFEE_ADD = 10 # 发单加佣金
ACCOUNT_LOG_TYPE_WITHDRAW_REFUND = 11 # 提款退款
ACCOUNT_LOG_TYPE_WITHDRAW_FEE = 12 # 提款手续费


ACCOUNT_LOG_DESC = {
        ACCOUNT_LOG_TYPE_FREEZE : "购彩",
        ACCOUNT_LOG_TYPE_PAID : "解冻",
        ACCOUNT_LOG_TYPE_PRIZE : "派奖",
        ACCOUNT_LOG_TYPE_CANCEL : "撤单",
        ACCOUNT_LOG_TYPE_RECHARGE : "充值",
        ACCOUNT_LOG_TYPE_WITHDRAW : "提款",
        ACCOUNT_LOG_TYPE_CHASEPAY : "追号",
        ACCOUNT_LOG_TYPE_CHASECANCEL : "追号退款",
        ACCOUNT_LOG_TYPE_FOLLOWFEE_SUB: "跟单佣金",
        ACCOUNT_LOG_TYPE_FOLLOWFEE_ADD: "发单佣金",
        ACCOUNT_LOG_TYPE_WITHDRAW_REFUND: "提款退款",
        ACCOUNT_LOG_TYPE_WITHDRAW_FEE: "提款手续费"
}


# 优惠券状态
COUPON_STATUS_EXPIRE = -1 # 优惠券已过期
COUPON_STATUS_UNUSE = 0   # 优惠券未使用
COUPON_STATUS_USED  = 1   # 优惠券已使用


# 消息任务表
MSG_TYPE_ORDER_PLACED   = 1 # 订单已下单，待支付
MSG_TYPE_ORDER_PAID     = 2 # 金额已冻结，待更新订单状态
MSG_TYPE_ORDER_SUCCPAY  = 3 # 订单成功支付，待拆票
MSG_TYPE_TICKET_SPLITED = 4 # 订单已拆票， 待出票
MSG_TYPE_TICKET_PRINTED = 5 # 已出票，待解冻扣款
MSG_TYPE_CHASENUMBER_PLACED = 6 # 追号已下单
MSG_TYPE_CHASENUMBER_PAID = 7 # 追号已支付

MSG_STATUS_NEW    = 0  # 新建消息
MSG_STATUS_DONE   = 1 # 处理完成


DEFIND_USER_LOGIN_TYPE = "mobile" #用户登录方式
DEFIND_LOGIN_SALT = "$nncp2018"
DEFIND_SMS_SALT = "$nncp2018sms"

DEFIND_VERDIFY_CODE_URL = "http://dev.api.tankonline.cn/nncp/v1.0/user/verifycode/img?deviceid={deviceid}&time={time}"

VTYPE_LOGIN = "login"
VTYPE_UNLOCK = "unlock"

#票描述
TICKET_STATUS_DESC = {
    TICKET_STATUS_SAVED: "已拆票",
    TICKET_STATUS_PRINTED: "已出票",
    TICKET_STATUS_PRIZED: "已中奖",
    TICKET_STAUTS_LOSE: "未中奖",
    TICKET_STATUS_CANCEL: "已撤单"
 }

#票描述
TICKET_JPRIZE_DESC = {
    TICKET_JPRIZE_UNCAL: "未算奖",
    TICKET_JPRIZE_PRIZE:"算奖已中奖",
    TICKET_JPRIZE_LOSE:"算奖未中奖",
    TICKET_JPRIZE_PRIZED: "中奖已派奖"
}

#方案描述
ORDER_STATUS_DESC = {
    ORDER_STATUS_FAILPAY: "支付失败",
    ORDER_STATUS_UNPAY: "未支付",
    ORDER_STATUS_SUCC: "未出票",
    ORDER_STATUS_PRINT_PART: "待开奖",#"部分出票",
    ORDER_STATUS_PRINT_ALL: "待开奖",#"全部出票",
    ORDER_STATUS_CANCEL: "全部撤单"
}


#方案中奖信息
ORDER_JPRIZE_DESC = {
    ORDER_JPRIZE_UNCAL: "未算奖",
    ORDER_JPRIZE_PRIZE: "已中奖",
    ORDER_JPRIZE_LOSE: "未中奖",
    ORDER_JPRIZE_PRIZED: "已派奖"
}


#彩种ID

LOTTE_DLT_ID = 28 #大乐透
LOTTE_SSQ_ID = 3#双色球
LOTTE_GX11X5_ID = 44 #广西11x5
LOTTE_JCZQ_ID = 46 #竞彩足球
LOTTE_JCLQ_ID = 47# 竞彩篮球

#彩种名称

LOTTE_NAME = {
    28: "大乐透",
    3: "双色球",
    44: "广西11选5",
    46: "竞彩足球",
    47: "竞彩篮球"
}

LOTTE_WTYPE_MAP = {
    28: [1,98,135,143,387,388,389],
     3: [2, 125, 377, 379],
    44: [244,245,246,247,248,249,250,251,252,253,254,255,256],
    46: [269,270,271,272,354,312,58],
    47: [274,275,276,277,313,58]
}

#
WEEK_NUM = {
    0: "周一",
    1: "周二",
    2: "周三",
    3: "周四",
    4: "周五",
    5: "周六",
    6: "周天"
}


PLAY_JQ_RESULT = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7+"
}

PLAY_SPF_RESULT = {
    "0": "负",
    "1": "平",
    "3": "胜"
}

WIN_SCORE = [
    '1:0',
    '2:0',
    '2:1',
    '3:0',
    '3:1',
    '3:2',
    '4:0',
    '4:1',
    '4:2',
    '5:0',
    '5:1',
    '5:2'
             ]

DRAW_SCORE = [
    '0:0',
    '1:1',
    '2:2',
    '3:3'
]

LOST_SCORE = [
    '0:1',
    '0:2',
    '1:2',
    '0:3',
    '1:3',
    '2:3',
    '0:4',
    '1:4',
    '2:4',
    '0:5',
    '1:5',
    '2:5'
]
PLAY_BF_RESULT = {
    '胜其它': '胜其它',
    '1:0': '1:0',
    '2:0': '2:0',
    '2:1': '2:1',
    '3:0': '3:0',
    '3:1': '3:1',
    '3:2': '3:2',
    '4:0': '4:0',
    '4:1': '4:1',
    '4:2': '4:2',
    '5:0': '5:0',
    '5:1': '5:1',
    '5:2': '5:2',
    '平其它': '平其它',
    '0:0': '0:0',
    '1:1': '1:1',
    '2:2': '2:2',
    '3:3': '3:3',
    '负其它': '负其它',
    '0:1': '0:1',
    '0:2': '0:2',
    '1:2': '1:2',
    '0:3': '0:3',
    '1:3': '1:3',
    '2:3': '2:3',
    '0:4': '0:4',
    '1:4': '1:4',
    '2:4': '2:4',
    '0:5': '0:5',
    '1:5': '1:5',
    '2:5': '2:5'
}

PLAY_BQC_RESULT = {
    '3-3': '胜胜',
    '3-1': '胜平',
    '3-0': '胜负',
    '1-3': '平胜',
    '1-1': '平平',
    '1-0': '平负',
    '0-3': '负胜',
    '0-1': '负平',
    '0-0': '负负'

}

WITHDRAW_STATUS_CREATE = 0 #提款订单
WITHDRAW_STATUS_CHECK = 1 #提款审核通过
WITHDRAW_STATUS_SUC = 2 #提款成功
WITHDRAW_STATUS_FAIL = -1 #提款失败
WITHDRAW_STATUS_REFUND = -2 #退款


WITHDRAW_FEE = 1 # 提款手续费

MQ_TICKET_EXCHANGE = 'nncp_ticket_print'
MQ_TICKET_ROUTING_KEY = 'nncp.key.ticket.print'
MQ_MSG_EXCHANGE = 'nncp_user_opreation'
MQ_MSG_ROUTING_KEYS = {
    'reg_suc': 'activity.key.user.reg.suc',
    'login_suc': 'activity.key.user.login.suc',
    'login_fail': 'activity.key.user.login.fail',
    'recharge_suc': 'activity.key.user.charge.suc',
    'buy_suc': 'activity.key.user.buy.suc',
    'print_suc': 'activity.key.project.print.suc',
    'prize_suc': 'activity.key.project.prize.suc'
}
