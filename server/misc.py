# -*- coding: utf-8 -*-

# This is also OK
# coding:utf-8
import json
import random
import string
import time as t
import requests
import logging as logger

from aes import encrypt, decrypt
from settings import api, log


def get(url):
    logger.info("req %s", url)
    begin = t.time()
    rsp = requests.get(url)
    log("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin))
    return rsp.ok and rsp.json() or None


def post(url, payload, with_common=False):
    if with_common:
        payload.update(common_data())
    log("req %s, params=%s" % (url, payload))
    begin = t.time()
    params = encrypt_data(payload)
    log("encrypt_data: %s" % params)
    rsp = requests.post(url, json=params)
    log("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin))
    if rsp:
        rsp = decrypt(rsp, api["key"], api["iv"])
    log("rsp from %s, text=%s, cost %s seconds" % (url, rsp, t.time() - begin))
    return rsp and json.loads(rsp) or None


def common_data():
    return {"nonce": "".join(random.sample(string.ascii_letters + string.digits, 10)), "timestamp": int(t.time())}


def encrypt_data(payload):
    return {"requestData": encrypt(payload, api["key"], api["iv"])}


if __name__ == "__main__":
    post("https://uatbotapi.drippay.net/mobile/transaction",
         {'accountAlias': '中国银行-LTT(李婷婷)-1535', 'balance': '13008.79', 'transactions': [
             {'amount': '2138.0', 'balance': '13008.79', 'customerAccount': '6225********2853', 'direction': '0',
              'flowNo': '', 'name': '杜 庆', 'postscript': '跨行转账', 'remark': '', 'sequence': '0',
              'time': '2021-07-28 17:54:58'},
             {'amount': '991.76', 'balance': '15146.79', 'customerAccount': '6214********3396', 'direction': '0',
              'flowNo': '', 'name': '周秋华', 'postscript': '跨行转账', 'remark': '', 'sequence': '1',
              'time': '2021-07-28 17:30:52'},
             {'amount': '2041.48', 'balance': '16138.55', 'customerAccount': '6217***********5775', 'direction': '0',
              'flowNo': '', 'name': '王卫峰', 'postscript': '转账支出', 'remark': '', 'sequence': '2',
              'time': '2021-07-28 17:28:53'}]})
