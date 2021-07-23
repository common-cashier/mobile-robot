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
from settings import api


def get(url):
    logger.info("req %s", url)
    begin = t.time()
    rsp = requests.get(url)
    logger.info("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin))
    return rsp.ok and rsp.json() or None


def post(url, payload, with_common=False):
    if with_common:
        payload.update(common_data())
    print("req %s, params=%s" % (url, payload))

    begin = t.time()
    params = encrypt_data(payload)
    print("encrypt_data: %s" % params)
    rsp = requests.post(url, json=params)
    print("rsp from %s, status=%s, text=%s, cost %s seconds" % (url, rsp.status_code, rsp.text, t.time() - begin))
    if rsp:
        rsp = decrypt(rsp, api["key"], api["iv"])
    print("rsp from %s, text=%s, cost %s seconds" % (url, rsp, t.time() - begin))
    return rsp and json.loads(rsp) or None


def common_data():
    return {"nonce": "".join(random.sample(string.ascii_letters + string.digits, 10)), "timestamp": int(t.time())}


def encrypt_data(payload):
    return {"requestData": encrypt(payload, api["key"], api["iv"])}


if __name__ == "__main__":
    post("https://uatbotapi.drippay.net/pc/last_transaction", {
        "accountAlias": "中国银行-LTT(李婷婷)-1535",
    })
