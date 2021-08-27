import json
import os

from flask import Flask, request
import settings
from models import BotUtil
from settings import gateway, serial_no, log

import uiautomator2 as u2
from bot_factory import BotFactory

app = Flask(__name__)

bot_util = BotUtil()


@app.route('/', methods=['GET'])
def hello():
    app.logger.log_text(serial_no)
    return serial_no


@app.route('/check_evn', methods=['GET'])
def check():
    try:
        ready = len(dir(u2)) > 100
        rsp = ready and {'code': 0, 'msg': '环境安装成功！'} or {'code': 1, 'msg': '环境安装失败，请重装！'}
        log('/check_env rsp: %s' % rsp)
    except ConnectionRefusedError:
        rsp = {'code': 2, 'msg': 'atx未启动，请先插上usb线，运行电脑脚本！'}
        log(rsp, settings.Level.SYSTEM)
    except Exception as ext:
        rsp = {'code': 1, 'msg': ext}
        log(rsp, settings.Level.SYSTEM)
    return rsp


@app.route('/status', methods=['POST'])
def status():
    if request.is_json:
        try:
            params = request.get_json()
            log('/status req: %s' % params)
            rsp = bot_util.cast_status(params)
            rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            log('/status rsp: %s' % rsp)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            log(rsp, settings.Level.SYSTEM)
        except Exception as ext:
            rsp = {'code': 1, 'msg': ext}
            log(rsp, settings.Level.SYSTEM)
        return rsp


@app.route('/last_transaction', methods=['POST'])
def last_transaction():
    if request.is_json:
        try:
            params = request.get_json()
            log('/last_transaction req: %s' % params)
            rsp = bot_util.cast_last_transaction(params)
            rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            log('/last_transaction rsp: %s' % rsp)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            log(rsp, settings.Level.SYSTEM)
        except Exception as ext:
            rsp = {'code': 1, 'msg': ext}
            log(rsp, settings.Level.SYSTEM)
        return rsp


@app.route('/transaction', methods=['POST'])
def transaction():
    if request.is_json:
        try:
            params = request.get_json()
            log('/transaction req: %s' % params)
            rsp = bot_util.cast_transaction(params)
            rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
            log('/transaction rsp: %s' % rsp)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            log(rsp, settings.Level.SYSTEM)
        except Exception as ext:
            rsp = {'code': 1, 'msg': ext}
            log(rsp, settings.Level.SYSTEM)
        return rsp


@app.route('/sms', methods=['POST'])
def sms():
    if request.is_json:
        try:
            params = request.get_json()
            print('/sms req: %s' % params)
            if not settings.last_sms == "" and settings.last_sms == params['sms']:
                ext = {'code': 1, 'msg': '短信已经接收，不接收重复短信'}
                print('/sms rsp: %s' % ext)
                return ext
            try:
                settings.last_sms = params['sms']
                rsp = bot_util.cast_sms(params)
                rsp = rsp is not None and rsp or {'code': 1, 'msg': '服务器未响应，请稍后再试!'}
                rsp = {'code': 0, 'msg': rsp}
                print('/sms rsp: %s ' % rsp)
                return rsp
            except Exception as ext:
                ext = {'code': 1, 'msg': str(ext)}
                print('/sms rsp: %s 需要先启动卡机' % ext)
                return ext
        except ConnectionRefusedError:
            ext = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            log(ext, settings.Level.SYSTEM)
            return ext


@app.route('/start', methods=['POST'])
def start():
    global rsp
    if request.is_json:
        try:
            # config = load_config()
            # if config is None or 'account' not in config:
            #     return {'code': 1, 'msg': '未绑定银行卡'}

            params = request.get_json()
            log('/start req: %s' % params)
            settings.api['base'] = params['baseURL']
            params['serialNo'] = settings.serial_no
            if params['kind'] == '0':
                if not params['bank'] in settings.receive_bank:
                    res = {"code": 1, 'msg': '收款暂时未支持您所启动的银行，请耐心等待开发！'}
                    log("check_bank: %s" % res)
                    return {"code": 1, 'msg': res}
            else:
                if not params['bank'] in settings.payment_bank:
                    res = {"code": 1, 'msg': '付款暂时未支持您所启动的银行，请耐心等待开发！'}
                    log("check_bank: %s" % res)
                    return res
            log("check_bank: is supported")
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
            bot_util.cast_sms = bot_factory.cast_sms
            rsp = bot_util.cast_start(params)
            rsp['data']['kind'] = params['kind']
            rsp['data']['devicesId'] = settings.serial_no
            settings.account_data = rsp['data']
            # if rsp is None or rsp['code'] != 0:
            #     return {'code': 1, 'msg': '获取银行卡信息失败'}
            log("rsp['data']: %s" % rsp)
            return {'code': 0, 'msg': '启动成功', 'data': rsp['data']}
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务未开启，请重新运行激活程序！'}
            log(rsp, settings.Level.SYSTEM)
        except Exception as ext:
            rsp = {'code': 1, 'msg': ext}
            log(rsp, settings.Level.SYSTEM)
            return rsp
        return {'code': 0, 'msg': '启动成功', 'data': rsp}


@app.route('/account_info', methods=['POST'])
def account_info():
    try:
        print('settings.account_data ---------> %s' % settings.account_data)
        bot_util.cast_account_info()
        rsp = settings.account_data
        log('/account_info rsp: %s' % rsp)
    except ConnectionRefusedError:
        rsp = {'code': 2, 'msg': 'atx未启动，请先插上usb线，运行电脑脚本！'}
        log(rsp, settings.Level.SYSTEM)
    except Exception as ext:
        rsp = {'code': 1, 'msg': ext}
        log(rsp, settings.Level.SYSTEM)
    return rsp


@app.route('/do_work', methods=['POST'])
def do_work():
    if request.is_json:
        try:
            params = request.get_json()
            log('/do_work req: %s' % params)
            if bot_util.cast_work is None:
                return {'code': 1, 'msg': '请先启动卡机！'}
            if params['do_work'] == "stop":
                msg = bot_util.cast_work(params)
                rsp = {'code': 0, 'msg': msg}
            else:
                bot_util.cast_work(params)
                rsp = {'code': 0, 'msg': '正在执行任务！'}
            log("do_work: %s" % params)
        except ConnectionRefusedError:
            rsp = {'code': 1, 'msg': '服务器异常，无法执行任务！'}
            log("{'code': 1, 'msg': '服务器异常，无法执行任务！'}", settings.Level.SYSTEM)
        except Exception as ext:
            rsp = {'code': 1, 'msg': ext}
            log(rsp, settings.Level.SYSTEM)
        return rsp


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
