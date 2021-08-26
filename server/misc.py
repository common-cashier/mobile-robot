# -*- coding: utf-8 -*-

# This is also OK
# coding:utf-8
import json
import random
import re
import string
import time as t
import requests
import logging as logger

from aes import encrypt, decrypt
from settings import api, log, sms_bank, Level


def get(url):
    logger.info("req %s", url)
    begin = t.time()
    rsp = requests.get(url)
    log("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin), Level.RES_WATER_DROP)
    return rsp.ok and rsp.json() or None


def post(url, payload, with_common=False):
    if with_common:
        payload.update(common_data())
    log("req %s, params=%s" % (url, payload), Level.REQ_WATER_DROP)
    begin = t.time()
    params = encrypt_data(payload)
    log("encrypt_data: %s" % params, Level.REQ_WATER_DROP)
    rsp = requests.post(url, json=params)
    log("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin), Level.RES_WATER_DROP)
    if rsp:
        rsp = decrypt(rsp, api["key"], api["iv"])
    log("rsp from %s, text=%s, cost %s seconds" % (url, rsp, t.time() - begin), Level.RES_WATER_DROP)
    return rsp and json.loads(rsp) or None


def common_data():
    return {"nonce": "".join(random.sample(string.ascii_letters + string.digits, 10)), "timestamp": int(t.time())}


def encrypt_data(payload):
    return {"requestData": encrypt(payload, api["key"], api["iv"])}


def parse_sms(sms_msg, bank):
    if re.findall(sms_bank[bank.upper()], sms_msg):
        if '交易码' in sms_msg:
            return re.findall(r'交易码(\d{6})', sms_msg)[0]
        elif '验证码' in sms_msg:
            return re.findall(r'验证码(\d{6})', sms_msg)[0]
        else:
            return 1
    else:
        return 1


if __name__ == "__main__":
    rsp = post("https://uatbotapi.drippay.net/pc/transfer",
         {'accountAlias': '中国银行-LTT(李婷婷)-1535'})
    print(rsp['data'])
    print(type(rsp['data']))
    print(rsp['data'] is None)

