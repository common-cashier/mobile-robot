# coding: utf-8
import json
from enum import Enum
from google.cloud import logging
import numpy as np

conf_file = 'config.json'
bot = None
post_sms_already = False
pc_url = ""
presser = {}
count = 0
account_data = ""

with open('../device_id.txt') as fd:
    serial_no = fd.readline().strip()

gateway = {
    'host': '0.0.0.0',
    'port': 5000,
}

root_service = {
    'host': '127.0.0.1',
    'port': 8081,
}
middle_url = "/mobile"
api = {
    'key': b'WLMjHQ7RAOqpzztV',
    'iv': b'WLMjHQ7RAOqpzztV',
    'ws': 'wss://bot-w.uatcashierapi.com/websocket',
    'base': 'https://bot-w.uatcashierapi.com',
    'register': '%s/register' % middle_url,
    'start': '%s/start' % middle_url,
    'status': '%s/status' % middle_url,
    'transfer': '%s/transfer' % middle_url,
    'transaction': '%s/transaction' % middle_url,
    'last_transaction': '%s/last_transaction' % middle_url,
    'upload_img_vc': '%s/upload_image_verify_code' % middle_url
}


class Status(Enum):
    IDLE = 0
    BOUND = 1
    STARTING = 2
    RUNNING = 3
    EXCEPTED = 4
    STOP = 5
    PAYING = 6


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


def log(msg, kind=0):
    logging_client = logging.Client()
    logger = logging_client.logger(serial_no)
    if kind == 1:
        logger.log_text(msg, severity="ERROR")
        print(msg)
    else:
        logger.log_text(msg)
        print(msg)
