import time

import uiautomator2 as u2
import settings
from models import Bot, Account, Transferee
from misc import parse_sms
from settings import log
import api


def convert(data, bank):
    settings.bot = Bot(serial_no=settings.serial_no, bank=bank, account=data['account'])
    settings.bot.account = Account(alias=data['accountAlias'], login_name=data['loginName'],
                                   login_pwd=data['loginPassword'],
                                   payment_pwd=data['payPassword'], key_pwd=data['keyPassword'],
                                   account=data['account'])
    print("set local account %s" % settings.bot.account)


def cast_query_order(alias):
    rsp = api.transfer(alias)
    if rsp['data'] is None:
        return False
    else:
        settings.transferee = Transferee(rsp['data']['orderId'], "%.2f" % (float(rsp['data']['amount']) / 100),
                                         rsp['data']['account'], rsp['data']['holder'])
        return True


class BotFactory:

    def __init__(self):
        self.d = u2.connect('0.0.0.0')
        # self.d = u2.connect('7d19caab')
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
        if params['do_work'] == "stop":
            api.status(params['account_alias'], settings.Status.IDLE)
            self.d.app_stop_all()
            # return self.bank.get_package()
        if params['do_work'] == "go_to_transfer":
            settings.order_exists = cast_query_order(settings.bot.account.alias)
        if params['do_work'] == "input_sms":
            return self.bank.input_sms(params['sms'])
        else:
            api.status(params['account_alias'], settings.Status.RUNNING)

        print("<--------------> %s" % params)
        self.bank.do_work(params['do_work'])
        self.doing = False

    def cast_sms(self, params):
        if self.doing:
            return False
        self.doing = True
        try:
            filter_msg = parse_sms(params['sms'], settings.bot.bank)
            if filter_msg != 1:
                self.doing = self.bank.input_sms(filter_msg)
            return filter_msg
        except Exception as ext:
            return ext

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
        params['balance'] = round(float(params['balance']) * 100, 2)
        for transaction in params['transactions']:
            print("last_time=%s transaction['time']=%s" % (last_time, transaction['time']))
            transaction['amount'] = "%.2f" % (float(transaction['amount']) * 100)
            transaction['balance'] = "%.2f" % (float(transaction['balance']) * 100)
            if transaction['time'] == last_time:
                break
            filter_transaction.append(transaction)
            i += i
        if len(filter_transaction) > 0:
            log('transaction_report: ' + str(filter_transaction), settings.Level.RECEIPT_OF_RECEIVE)
            rsp = api.transaction(params['account_alias'], params['balance'], filter_transaction)
            api.status(params['account_alias'], settings.Status.RUNNING)
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
        api.status(params['account_alias'], settings.Status.RUNNING)
        self.doing = False
        return rsp

