# coding: utf-8
from settings import api, Status
import misc


def start(account_alias):
    return post(api['start'], {'accountAlias': account_alias})


def status(account_alias, state):
    return post(api['status'], {'accountAlias': account_alias, 'status': state.value})


def last_transaction(account_alias):
    return post(api['last_transaction'], {'accountAlias': account_alias})


def transfer(account_alias):
    return post(api['transfer'], {'accountAlias': account_alias})


def transaction(account_alias, balance, transactions):
    return post(api['transaction'], {'accountAlias': account_alias, 'balance': balance, 'transactions': transactions})


def transfer_result(order_id, order_status, msg=''):
    return post(api['transfer_result'], {'orderId': order_id, 'status': order_status, 'msg': msg})


def receipt(account_alias, receipts):
    return post(api['receipt'], {'accountAlias': account_alias, "receipts": receipts})


def post(url, payload):
    url = api['base'] + url
    print('-------------------> %s' % url)
    return misc.post(url, payload, False)


if __name__ == '__main__':
    # data = {'serialNo': 'xxxx', 'accountAlias': 'dddd'}
    # data.update(common_data())
    # print(data)
    # print(register("1ad2838c0107", "农业银行-LYF(刘亦菲)-8888"))
    print(start('RR8M90JGAXR', '农业银行-WQ(韦强)-0873'))
    # print(status('RR8M90JGAXR', Status.RUNNING.value))
    # print(transfer_status(94, 0)
    pass
