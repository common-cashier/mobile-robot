import json
import logging
import os

from flask import Flask, request
import settings
import api
from models import Account, Transaction, Bot, BotUtil
from settings import gateway, serial_no
import logging as logger
import uiautomator2 as u2
from bot_factory import BotFactory

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

bot_util = BotUtil()


@app.route('/', methods=['GET'])
def hello():
    app.logger.info(serial_no)
    return serial_no


@app.route('/check_evn', methods=['GET'])
def check():
    try:
        ready = len(dir(u2)) > 100
        res = ready and {'code': 0, 'msg': '环境安装成功！'} or {'code': 1, 'msg': '环境安装失败，请重装！'}
        logger.info('/check_env rsp: %s', res)
    except ConnectionRefusedError:
        res = {'code': 2, 'msg': 'atx未启动，请先插上usb线，运行电脑脚本！'}
        app.logger.info('/check_env rsp: %s', res)
    return res


@app.route('/status', methods=['POST'])
def status():
    if request.is_json:
        try:
            params = request.get_json()
            logger.info('/status req: %s', params)
            rsp = bot_util.cast_status(params)
            res = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            logger.info('/status rsp: %s', res)
        except ConnectionRefusedError:
            res = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            logger.info('/status rsp: %s', res)
        return res


@app.route('/last_transaction', methods=['POST'])
def last_transaction():
    if request.is_json:
        try:
            params = request.get_json()
            logger.info('/last_transaction req: %s', params)
            rsp = bot_util.cast_last_transaction(params)
            rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            logger.info('/last_transaction rsp: %s', rsp)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            logger.info('/last_transaction rsp: %s', rsp)
        return rsp


@app.route('/transaction', methods=['POST'])
def transaction():
    if request.is_json:
        try:
            params = request.get_json()
            logger.info('/transaction req: %s', params)
            rsp = bot_util.cast_transaction(params)
            rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            logger.info('/transaction rsp: %s', rsp)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            logger.info('/transaction rsp: %s', rsp)
        return rsp


@app.route('/start', methods=['POST'])
def start():
    global rsp
    if request.is_json:
        try:
            # config = load_config()
            # if config is None or 'account' not in config:
            #     return {'code': 1, 'msg': '未绑定银行卡'}

            params = request.get_json()
            logger.info('/start req: %s', params)
            settings.api['base'] = params['baseURL']
            logger.info('/start req: %s', params)

            # 假数据
            # data = {
            #     "accountAlias": "中国银行-BOC(徐秀策)-4249）",
            #     "loginName": "18648890160",
            #     "loginPassword": "aa080706",
            #     "paymentPassword": "080706",
            #     "ukeyPassword": "080706",
            #     "bank": "BOC"
            # }
            # data_obj = convert(data=data)

            bot_factory = BotFactory()
            bot_util.cast_status = bot_factory.cast_status
            bot_util.cast_last_transaction = bot_factory.cast_last_transaction
            bot_util.cast_transaction = bot_factory.cast_transaction
            bot_util.cast_work = bot_factory.cast_work
            bot_util.cast_start = bot_factory.cast_start
            bot_util.cast_account_info = bot_factory.cast_account_info
            rsp = bot_util.cast_start(params)
            settings.account_data = rsp['data']
            # if rsp is None or rsp['code'] != 0:
            #     return {'code': 1, 'msg': '获取银行卡信息失败'}
            print("rsp['data']: %s" % rsp['data'])
            return {'code': 0, 'msg': '启动成功', 'data': rsp}
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            logger.info('/start rsp: %s', rsp)
        except Exception:
            return {'code': 0, 'msg': '启动成功', 'data': rsp}
        return {'code': 0, 'msg': '启动成功', 'data': rsp}


@app.route('/account_info', methods=['POST'])
def account_info():
    try:
        print('settings.account_data ---------> %s' % settings.account_data)
        bot_util.cast_account_info()
        res = settings.account_data
        # app.logger.info('/account_info rsp: %s', res)
    except ConnectionRefusedError:
        res = {'code': 2, 'msg': 'atx未启动，请先插上usb线，运行电脑脚本！'}
        app.logger.info('/account_info rsp: %s', res)
    return res


@app.route('/stop', methods=['GET'])
def stop():
    bot_util.cast_stop()


@app.route('/do_work', methods=['POST'])
def do_work():
    if request.is_json:
        try:
            params = request.get_json()
            logger.info('/do_work req: %s', params)
            bot_util.cast_work(params)
            res = {'code': 0, 'msg': '正在执行任务！'}
        except ConnectionRefusedError:
            res = {'code': 1, 'msg': '服务器异常，无法执行任务！'}
        return res


def update_config(api_url, account):
    settings.api['base'] = api_url
    ws = os.path.join('wss://' + api_url.split("https://")[1], 'websocket')
    settings.api['ws'] = ws

    with open(settings.conf_file, 'w') as conf:
        conf.write(json.dumps({'api': {'base': api_url, 'ws': ws}, 'account': {'alias': account}}))


def load_config():
    if os.path.exists(settings.conf_file):
        with open(settings.conf_file, 'r') as conf:
            config = json.loads(conf.read())
            api_url = config['api']['base']
            settings.api['base'] = api_url
            settings.api['ws'] = os.path.join(api_url.replace('http', 'ws'), 'websocket')
            return config
    return None


if __name__ == '__main__':
    app.run(host=gateway['host'], port=gateway['port'])
