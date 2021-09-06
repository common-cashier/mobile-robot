class Bot:
    def __init__(self, serial_no=None, device=None, bank=None, account=None, trans=None, last_trans=None):
        self.serial_no = serial_no
        self.device = device
        self.bank = bank
        self.account = account  # Account
        self.trans = trans  # AccountTrans
        self.last_trans = last_trans
        self.payment = False  # mode[receiving, payment]
        self.running = True
        self.pid = 0
        self.device_info = None

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Account:
    def __init__(self, alias=None, login_name=None, login_pwd=None, payment_pwd=None, key_pwd=None, currency=None,
                 account=None):
        self.alias = alias
        self.login_name = login_name
        self.login_pwd = login_pwd
        self.payment_pwd = payment_pwd
        self.key_pwd = key_pwd
        self.currency = currency
        self.account = account


class Transferee:
    def __init__(self, order_id=None, amount=None, account=None, holder=None, bank_name=None, branch=None):
        self.order_id = order_id
        self.amount = amount
        self.account = account
        self.holder = holder
        self.bank_name = bank_name
        self.branch = branch

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __repr__(self):
        return self.__str__()


# class AccountTrans:
#     def __init__(self, last_trans=None, trans=None):
#         if trans is None:
#             trans = []
#         self.last_trans = last_trans  # Transaction
#         self.trans = trans  # [Transaction]
#         self.next_page = True  # if it is need to turn to next page
#
#     def __str__(self):
#         return str(self.__class__) + ": " + str(self.__dict__)
#
#     def __repr__(self):
#         return self.__str__()


class Transaction:
    def __init__(self, trans_time, trans_type=None, name=None, amount=None, balance=None, postscript=None, account=None,
                 summary=None):
        self.trans_time = trans_time
        self.trans_type = trans_type
        self.name = name
        self.amount = amount
        self.balance = balance
        self.postscript = postscript
        self.account = account
        self.summary = summary

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class BotUtil:
    def __init__(self, cast_transaction=None, cast_status=None, cast_start=None, cast_last_transaction=None,
                 cast_work=None, cast_account_info=None, cast_sms=None):
        self.cast_transaction = cast_transaction
        self.cast_status = cast_status
        self.cast_last_transaction = cast_last_transaction
        self.cast_transaction = cast_transaction
        self.cast_work = cast_work
        self.cast_start = cast_start
        self.cast_account_info = cast_account_info
        self.cast_sms = cast_sms


class Receipt:
    def __init__(self, time=None, amount=None, name=None, postscript=None, customerAccount=None, inner=None,
                 flowNo=None, sequence=None):
        self.time = time
        self.amount = amount
        self.name = name
        self.postscript = postscript
        self.customerAccount = customerAccount
        self.inner = inner
        self.flowNo = flowNo
        self.sequence = sequence
