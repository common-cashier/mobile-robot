import datetime
import time

import uiautomator2 as u2
import settings
from models import Bot, Account, Transferee, Receipt
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
    if settings.debug:
        # 测试代码
        # settings.transferee = Transferee('32422', '1.01', '6217852600028354869', '张源花')
        return False
    else:
        # 线上代码
        rsp = api.transfer(alias)
        if rsp['data'] is None:
            return False
        else:
            settings.transferee = Transferee(rsp['data']['orderId'], "%.2f" % (float(rsp['data']['amount']) / 100),
                                             rsp['data']['account'], rsp['data']['holder'])
            return True


def report_transaction(params):
    last = api.last_transaction(params['account_alias'])
    last_time = last['data']['time']
    print("<<<<<-------------->>>>>>> %s" % last_time)
    i = 0
    filter_transaction = []
    params['balance'] = "%.2f" % (float(params['balance']) * 100)
    for transaction in params['transactions']:
        transaction['time'] = day_filter(transaction['time'])
        print("last_time=%s transaction['time']=%s" % (last_time, transaction['time']))
        #  查看是否需要回单
        if settings.need_receipt and settings.bot.bank.lower() == 'boc':
            filter_receipt(transaction)
        # 改变单位适应水滴
        transaction['amount'] = "%.2f" % (float(transaction['amount']) * 100)
        transaction['balance'] = "%.2f" % (float(transaction['balance']) * 100)
        # 查看服务器最后一条
        if transaction['time'] == last_time and transaction['amount'] == "%.2f" % (float(last['data']['amount'])):
            break
        filter_transaction.append(transaction)
        i += i
    time.sleep(1)
    if len(filter_transaction) > 0:
        log('transaction_report: ' + str(filter_transaction), settings.Level.RECEIPT_OF_RECEIVE)
        api.transaction(params['account_alias'], params['balance'], filter_transaction)
        api.status(params['account_alias'], settings.Status.RUNNING)
    if settings.bot.bank.lower() == 'boc':
        report_receipt(params)


def filter_receipt(transaction):
    print('need_receipt: %s -- %s' % (str(settings.last_transferee), str(transaction)))
    transaction_time = datetime.datetime.strptime(transaction['time'], '%Y-%m-%d %H:%M:%S')
    if settings.last_transferee.amount == "%.2f" % (
            float(transaction['amount'])) and settings.last_transferee.holder == transaction['name'] and (
            settings.payment_time <= transaction_time < (
            settings.payment_time + datetime.timedelta(minutes=20))):
        log('need_receipt_compare: transferee_amount:%s = transaction_amount:%s -- holder:%s = name:%s' % (
            settings.last_transferee.amount, transaction['amount'], settings.last_transferee.holder,
            transaction['name']), settings.Level.RECEIPT)
        inner = True
        if transaction['postscript'] == '跨行转账':
            inner = False
        settings.receipt = settings.receipt_no
        settings.receipt_no = Receipt()
        settings.receipt.time = transaction['time']
        settings.receipt.postscript = transaction['postscript']
        settings.receipt.inner = inner
        settings.receipt.sequence = transaction['sequence']
        settings.need_receipt = False


def report_receipt(params):
    if settings.receipt.name is not None:
        try:
            api.receipt(params['account_alias'], [
                {'time': settings.receipt.time, 'amount': "%.2f" % (float(settings.receipt.amount) * 100),
                 'name': settings.receipt.name,
                 'postscript': settings.receipt.postscript, 'customerAccount': settings.receipt.customerAccount,
                 'inner': settings.receipt.inner, 'flowNo': settings.receipt.flowNo,
                 'sequence': settings.receipt.sequence, 'format': settings.receipt.format,
                 'billNo': settings.receipt.billNo, 'imageFormat': settings.receipt.imageFormat,
                 'content': settings.receipt.content}])
        except Exception as ext:
            log(ext, settings.Level.SYSTEM)
        settings.receipt = Receipt()
    settings.need_receipt = False


def day_filter(time_str):
    arr = time_str.split('-')
    date_time = arr[2].split(' ')
    day = date_time[0]
    if len(day) > 2:
        day = day[1:]
        date = arr[0] + '-' + arr[1] + '-' + day + ' ' + date_time[1]
        print('before date: %s last date: %s' % (time_str, date))
        return date
    else:
        return time_str


class BotFactory:

    def __init__(self):
        if settings.debug:
            # 测试代码
            self.d = u2.connect('7d19caab')
        else:
            # 线上代码
            self.d = u2.connect('0.0.0.0')
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

    def cast_start(self, params):
        if self.doing:
            return False
        self.doing = True
        if params['devices_id'] is not None and params['devices_id'] != '':
            rsp = api.start(params['account_alias'], params['devices_id'])
        else:
            rsp = api.start(params['account_alias'])
        if rsp['code'] == 0 and rsp['data'] is not None:
            convert(rsp['data'], params['bank'].lower())
            log("rsp['data']: %s" % rsp)
            self.doing = False
            return rsp
        else:
            self.doing = False
            return {'code': 1, 'msg': rsp['msg'], 'data': rsp['data']}

    def cast_work(self, params):
        if params['do_work'] == "stop":
            if self.bank == '':
                return {'code': 0, 'msg': '卡机状态已经上报！'}
            else:
                self.bank.do_work(params['do_work'])
            return
        if self.doing:
            return False
        self.doing = True
        if params['do_work'] == "start":
            settings.bot.device_info = self.d.info
            settings.bot.device = self.d
            module = __import__("bots.%s" % settings.bot.bank.lower())
            robot = getattr(module, settings.bot.bank.lower())
            self.bank = robot
        if params['do_work'] == "go_to_transfer":
            if settings.need_receipt_no:
                self.bank.do_work('go_to_receipt')
            else:
                if settings.need_receipt:
                    self.bank.do_work('go_to_transaction')
                else:
                    query_order = cast_query_order(settings.bot.account.alias)
                    if not query_order:
                        self.bank.do_work('go_to_transaction')
                    else:
                        self.bank.do_work('transfer')

            api.status(params['account_alias'], settings.Status.RUNNING)
            self.doing = False
            return False
        if params['do_work'] == "input_sms":
            return self.bank.input_sms(params['sms'])
        else:
            api.status(params['account_alias'], settings.Status.RUNNING)
        print("do_work:print: %s" % params)
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
        report_transaction(params)
        self.doing = False
        time.sleep(1)
        self.bank.do_work("back")
        time.sleep(1)
        self.bank.do_work("back")
        return rsp

    def cast_last_transaction(self, params):
        if self.doing:
            return False
        self.doing = True
        rsp = api.last_transaction(params['account_alias'])
        api.status(params['account_alias'], settings.Status.RUNNING)
        self.doing = False
        return rsp
