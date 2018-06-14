# -*- coding:utf-8 -*-
# Python2.7.12
import binascii
from pyDes import des, ECB, PAD_PKCS5
def des_encrypt(s, key):
    iv = key
    k = des(key, ECB,iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)

def des_descrpt(s, key):
    iv = key
    k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de

if __name__ == '__main__':
    user = 'liumingqi@iie.ac.cn'
    user_sub = user[0:8]
    str_en = des_encrypt('liumingqi0709', user_sub)
    print str_en.upper()
    user = "abc@bupt.edu.cn"
    pwd = "abc007002"
    str_en = des_encrypt(pwd, user[0:8])
    print str_en.upper()
    user_sub = user[0:8]
    str_de = des_descrpt(str_en, user_sub)
    print str_de



