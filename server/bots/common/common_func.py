import datetime
import os
import time

from server import settings
from server import api
from server.bot_factory import report_transaction
from server.models import Transaction, TransactionFactory


def start(self, package):
    self.screen_on()
    settings.bot.pid = self.app_start(package)
    return self.app_wait(package)  # 等待应用运行, return pid(int)


def stop(self, package):
    self.sleep(1)
    self.app_stop(package)
    self.app_stop('com.termux')


def reset_temp_transaction():
    settings.temp_transaction = []
    settings.got_transaction = []
    settings.last_transaction_list = []
    settings.check_transaction = False


def got_filter_transaction():
    for item in settings.temp_transaction:
        if item != {} and item not in settings.total_transaction:
            settings.total_transaction.append(item)
    reset_temp_transaction()


def get_last_transaction():
    last = api.last_transaction(settings.bot.account.alias)
    print('----> res <---- %s' % last)
    now = datetime.datetime.now()
    last_time = datetime.datetime.strptime(last['data']['time'], '%Y-%m-%d %H:%M:%S')
    print('start compare')
    if time_compare(now, last_time) > 24:
        print('over a day')
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        last['data']['time'] = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        print('reset last time')
    print('use normal last time')
    return last


def time_compare(day1, day2):
    delta = day1 - day2
    print("所有秒数： %s" % delta.total_seconds())
    return delta.total_seconds() / 60 / 60


def make_transaction(self, bank_transaction):
    print('make_transaction')
    last = get_last_transaction()
    print('got last')
    time.sleep(3)
    settings.got_transaction = bank_transaction.get_transaction(last)
    if settings.middle_break:
        settings.middle_break = False
        return
    if settings.last_transferee != [] and (settings.last_transaction_list == settings.got_transaction or settings.got_transaction[-1] in settings.last_transaction_list):
        got_filter_transaction()
    else:
        settings.last_transaction_list = settings.got_transaction
        for ele in settings.got_transaction:
            settings.temp_transaction.append(ele)
        self.sleep(1)
        self.swipe_ext("up", scale=0.4)
        self.sleep(1)


def check_report_transactions(self, bank_transaction: TransactionFactory):
    settings.check_transaction = True
    while settings.check_transaction:
        make_transaction(self, bank_transaction)
    print('settings.total_transaction: %s' % settings.total_transaction)
    if len(settings.total_transaction) > 0:
        params = {'account_alias': settings.bot.account.alias,
                  'balance': settings.total_transaction[0]['balance'],
                  'transactions': settings.total_transaction}
        report_transaction(params)
        settings.total_transaction = []


def money_format(amount):
    res = format(float(amount), ",")
    if len(res.split('.')[1]) < 2:
        res = res + '0'
    return res


def make_common_transaction(d, last, transaction_arr, transaction_flag, check_detail_page, make_ele):
    transaction = []
    a = 0
    last_time = last['data']['time']
    for elem in d.xpath(transaction_arr).all():
        if elem.attrib['resource-id'] == transaction_flag:
            print('id-amount', elem.attrib['resource-id'])
            elem.click()
            if check_detail_page():
                transaction.append({})
                transaction_ele: Transaction = make_ele()
                print('ele time: %s last time: %s 相等：%s ele amount: %s last amount: %s' % (
                    transaction_ele.time, last_time, str(transaction_ele.time == last_time), "%.2f" % (float(transaction_ele.amount) * 100),
                    "%.2f" % (float(last['data']['amount']))))

                def finish_transaction():
                    if len(transaction) > 0:
                        for ele in transaction:
                            settings.temp_transaction.append(ele)
                        got_filter_transaction()
                    settings.middle_break = True

                if transaction_ele.time == last_time:
                    finish_transaction()
                    return transaction
                if time_compare(datetime.datetime.strptime(transaction_ele.time, '%Y-%m-%d %H:%M:%S'),
                                datetime.datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')) > 24:
                    finish_transaction()
                    return transaction
                else:
                    transaction[a] = transaction_ele.to_dict(True)
                    a += 1

    last_index = len(transaction) - 1
    if transaction[last_index] == {}:
        del transaction[last_index]
    print('get_transaction: %s' % transaction)
    return transaction


# 获取最新文件
def get_file_list(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
        print(dir_list)
        return dir_list
