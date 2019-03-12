# coding: utf-8

from Crypto.Cipher import ARC4 as RC4


TYPE_DT1 = 'DT1'



class Rc4V1(object):
    """RC4加密
    """

    def __init__(self, secret):
        """初始化
        @param secret: secret的长度一般为32位，
                假设secret为"abcdefghijklmnopqrstuvwxyz123456"，
                得到的_secret为"ghijklmnopqrstuvklmnopqrstuvwxyz"
        """
        self._secret = secret[6:-10] + secret[10:-6]
        self._encoder = RC4.new(self._secret)
        self._decoder = RC4.new(self._secret)

    def encrypt(self, content):
        return self._encoder.encrypt(content)

    def decrypt(self, content):
        return self._decoder.decrypt(content)




ciphers = {
    TYPE_DT1 : Rc4V1,
}


def new(cid, *args, **kwargs):
    return ciphers[cid](*args, **kwargs)

