# coding: utf-8
import datetime
import json
import os
from enum import Enum
import numpy as np

from models import Transferee
from sls_quick_start import put_logs

conf_file = 'config.json'
bot = None
post_sms_already = False
pc_url = ""
presser = {}
count = 0
account_data = ""
last_sms = ""
order_exists = True
transferee = ""
log_msg = ""

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
middle_url = "/pc"
bank_map = {
    'CCB': '中国建设银行',
    'ICBC': '中国工商银行',
    'ABC': '中国农业银行',
    'BOCSH': '中国银行',
    'BCM': '交通银行',
    'CMB': '招商银行',
    'MSB': '中国民生银行',
    'CITTIC': '中信银行',
    'SHPDB': '上海浦东发展银行',
    'PAB': '平安银行（原深圳发展银行）',
    'INB': '兴业银行',
    'EBB': '中国光大银行',
    'GDB': '广发银行股份有限公司',
    'HXB': '华夏银行',
    'PSBC': '中国邮政储蓄银行',
    'BOS': '上海银行',
    'JSBK': '江苏银行股份有限公司',
}
sms_bank = {
    'CCB': r'\[建设银行]$',
    'ABC': r'^【中国农业银行】',
    'ICBC': r'【工商银行】$',
    'GXRCU': r'^【广西农信】',
    'XXC': r'\[兴业银行]$',
    'BOC': r'【中国银行】$'
}
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
    'upload_img_vc': '%s/upload_image_verify_code' % middle_url,
    'transfer_result': '%s/transfer_result' % middle_url
}

payment_bank = [
    'BOC'
]

receive_bank = [
    'BOC'
]


class Status(Enum):
    # 空闲
    IDLE = 0
    # 启动中
    STARTING = 1
    # 运行中
    RUNNING = 2
    # 异常
    EXCEPTED = 3
    # 暂停
    PAUSE = 4
    # 冻结
    WARNING = 5


class Level(Enum):
    # app调用的
    APP = 0
    # 系统出错的
    SYSTEM = 1
    # 请求水滴服务器的
    REQ_WATER_DROP = 2
    # 水滴服务器返回的
    RES_WATER_DROP = 3
    # 外部api的
    EXTERNAL = 4
    # 收款凭证
    RECEIPT_OF_RECEIVE = 5
    # 付款凭证
    RECEIPT_OF_PAYMENT = 6


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


import logging


def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger

if not os.path.exists('log'):
    os.mkdir('log')
today = datetime.date.today()
logger = logger_config(log_path='./log/%s.txt' % today, logging_name='水滴手机自动机')


# 向Logstore写入数据。
# level 0是app调用的
# level 1是系统出错的
# level 2是请求水滴服务器的
# level 3是水滴服务器返回的
# level 4是外部api的
# level 5是收款凭证
# level 6是付款凭证
def log(msg, kind=Level.APP):
    global log_msg
    if not log_msg == "" and log_msg == msg:
        return
    else:
        log_msg = msg
    level_arr = ['App调用', '系统出错', '请求水滴服务器', '水滴服务器返回值', '外部Api', '收款凭证', '付款凭证']
    put_logs(serial_no, msg, level_arr[kind.value])
    msg = "%s - %s" % (level_arr[kind.value], msg)
    logger.warning(msg)


if __name__ == "__main__":
    print(datetime.datetime.now())
