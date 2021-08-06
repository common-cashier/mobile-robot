import json
import time

import uiautomator2 as u2
import settings
from models import Bot, Account, Transaction
from settings import Status
import api


def convert(data, bank):
    settings.bot = Bot(serial_no=settings.serial_no, bank=bank, account=data['account'])
    settings.bot.account = Account(alias=data['accountAlias'], login_name=data['loginName'],
                                   login_pwd=data['loginPassword'],
                                   payment_pwd=data['payPassword'], key_pwd=data['keyPassword'])
    print("---------------?account %s" % settings.bot.account)
    print("---------------?account %s" % type(settings.bot.account))
    # if 'lastTrans' in data and data['lastTrans']:
    #     tran = data['lastTrans']
    #     trans = Transaction(trans_time=tran['time'], trans_type=tran['direction'], name=tran['name'],
    #                         amount=tran['amount'], balance=tran['balance'], postscript=tran['postscript'])
    #     settings.bot.last_trans = trans


class BotFactory:

    def __init__(self):
        self.d = u2.connect('0.0.0.0')
        # self.d = u2.connect('172ddafa')
        print('bot: %s' % settings.bot)
        self.bank = ""
        print("您的银行应用已经由脚本接管")
        self.doing = False

    def cast_status(self, params):
        if self.doing:
            return False
        self.doing = True
        rsp = api.status(params['account_alias'], params['status'])
        self.doing = False
        return rsp

    def cast_account_info(self):
        if self.doing:
            return False
        self.doing = True
        settings.account_data = {'code': 0, 'msg': '成功', 'data': settings.account_data}
        self.doing = False

    def cast_start(self, params):
        if self.doing:
            return False
        self.doing = True
        rsp = api.start(params['account_alias'])
        # api.status(params['account_alias'], '2')
        convert(rsp['data'], params['bank'].lower())
        self.doing = False
        return rsp

    def cast_work(self, params):
        if self.doing:
            return False
        self.doing = True
        if params['do_work'] == "start":
            settings.bot.device_info = self.d.info
            settings.bot.device = self.d
            module = __import__("bots.%s" % settings.bot.bank.lower())
            robot = getattr(module, settings.bot.bank.lower())
            self.bank = robot
        self.bank.do_work(params['do_work'])
        print("<--------------> %s" % params)
        api.status(params['account_alias'], '2')
        self.doing = False

    def cast_transaction(self, params):
        rsp = {"code": "0", "msg": "上传的流水已存在"}
        if self.doing:
            return False
        self.doing = True
        last = api.last_transaction(params['account_alias'])
        last_time = last['data']['time']
        print("<<<<<-------------->>>>>>> %s" % last_time)
        i = 0
        filter_transaction = []
        for transaction in params['transactions']:
            print("last_time=%s transaction['time']=%s" % (last_time, transaction['time']))
            if transaction['time'] == "last_time":
                break
            filter_transaction.append(transaction)
            i += i
        if len(filter_transaction) > 0:
            rsp = api.transaction(params['account_alias'], params['balance'], filter_transaction)
            api.status(params['account_alias'], '2')
        self.bank.do_work("back")
        time.sleep(1)
        self.bank.do_work("back")
        self.doing = False
        return rsp

    def cast_last_transaction(self, params):
        if self.doing:
            return False
        self.doing = True
        rsp = api.last_transaction(params['account_alias'])
        api.status(params['account_alias'], '2')
        self.doing = False
        return rsp
