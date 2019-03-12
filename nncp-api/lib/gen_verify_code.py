#coding=utf-8


try:
    import captchaimage
except:
    pass

try:
    from PIL import Image
except:
    import Image

import traceback
import cStringIO
import time
import random

#from route import Router
import define
from dbpool import db_pool
from util.configer import *
import rediskey
from util.tools import Log
logger = Log().getLog()

#加载配置
configs = {}
def set_up(confs):
    configs.update(confs)

try:
    JsonConfiger.get_instance().register_auto_updater(set_up, 'files')
except Exception as ex:
    logger.error(traceback.format_exc())

def get_img_url(deviceid):
    return configs.get("img_url", "").format(deviceid=deviceid, time=time.time())

def get_img(code):
    """
    获取验证图片
    """
    img_file = None
    try:
        background_color = (255, 255, 255)
        text_color = random.choice(((27, 78, 181), (22, 163, 35), (214, 36, 7)))  # blue, green, red
        size_y = 44
        image_data = captchaimage.create_image(configs["kxfont"], 22, size_y, code)
        size_x = len(image_data) / size_y
        mask_im = Image.frombytes("L", (size_x, size_y), image_data)
        img_file = cStringIO.StringIO()
        target_im = Image.new("RGB", (size_x, size_y), text_color)
        target_im.paste(background_color, (0, 0), mask_im)
        target_im.save(img_file, "PNG")
        img = img_file.getvalue()
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        if img_file:
            img_file.close()
    return img

class GenVerifyCode(object):
    """生成验证码
    """

    def get_verify_code_img(self, params):
        """获取验证码图片
        """
        deviceid = params.get("deviceid", "")
        username = params.get("username", "")
        vtype = params.get("vtype", define.VTYPE_LOGIN)
        redis_opt = db_pool.get_redis("main")
        code = ""
        for i in range(4):
            code += chr(random.randrange(ord('a'), ord('z')+1))

        vkey = deviceid # 默认的验证码key用设备码
        if vtype == define.VTYPE_LOGIN:
            # 登陆
            vkey = deviceid
        elif vtype == define.VTYPE_UNLOCK:
            # 解锁
            vkey = username
        logger.debug(vkey)
        rds_name = rediskey.CRAZY_VERIFY_CODE_PREFIX.format(vtype=vtype, vkey=vkey)
        redis_opt.set(rds_name, code, ex=5 * 60)
        logger.info("rds_name=%s|code=%s|deviceid=%s|username=%s", rds_name, code, deviceid, username)
        img = get_img(code)
        return img
