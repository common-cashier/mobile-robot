import abc
from _datetime import datetime
from abc import abstractmethod
from typing import Callable, Union

from server.common_helpers import DateTimeHelper, StrHelper


def amount_to_fen(amount: Union[str, float]) -> int:
    """分单位金额整数型数值"""
    # 17.65 * 100
    return int(round(float(amount) * 100))


def amount_to_yuan(amount: Union[str, int, float]) -> float:
    """元单位金额浮点型数值"""
    return round(float(amount) / 100, 2)  # 四舍五入，保留2位小数


def amount_to_yuan_str(amount: Union[str, int, float]) -> str:
    """元单位金额字符串格式"""
    return '{0:.2f}'.format(amount_to_yuan(amount))


def format_datetime(_dt: Union[datetime, str]) -> str:
    """格式化时间字符串，后台接收格式"""
    return DateTimeHelper.to_str(_dt, '%Y-%m-%d %H:%M:%S')


# 账户信息模型
class Account:
    def __init__(self, alias: str = '', login_name: str = '', login_pwd: str = '', payment_pwd: str = '',
                 key_pwd: str = '', currency: str = '', account: str = ''):
        self.alias = alias
        self.login_name = login_name
        self.login_pwd = login_pwd
        self.payment_pwd = payment_pwd
        self.key_pwd = key_pwd
        self.currency = currency
        self.account = account

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    @staticmethod
    def from_dict(dict_data: dict):
        return Account(alias=dict_data['accountAlias'], login_name=dict_data['loginName'],
                       login_pwd=dict_data['loginPassword'],
                       payment_pwd=dict_data['payPassword'], key_pwd=dict_data['keyPassword'],
                       account=dict_data['account'])


# 转账账户信息模型
class Transferee:
    def __init__(self, order_id: int = 0, amount: float = 0, account: str = '', holder: str = '', bank_name: str = '',
                 branch: str = '', postscript: str = ''):
        self.order_id = order_id
        self.amount = amount  # 带小数点的分单位值
        self.account = account
        self.holder = holder
        self.bank_name = bank_name
        self.branch = branch
        self.postscript = postscript

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def amount_yuan(self) -> float:
        return amount_to_yuan(self.amount)

    def amount_yuan_str(self) -> str:
        return amount_to_yuan_str(self.amount)

    @staticmethod
    def from_dict(dict_data: dict):
        return Transferee(order_id=dict_data['orderId'], amount=dict_data['amount'],
                          account=dict_data['account'], holder=dict_data['holder'],
                          postscript=dict_data['postscript'], bank_name=dict_data['bankName'],
                          branch=dict_data['branch'])


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


# 流水信息模型
class Transaction:
    def __init__(self, customer_account: str = '', time: str = '', direction: int = 0, name: str = '',
                 amount: int = 0, balance: int = 0, postscript: str = '', sequence: int = 0, extension: dict = None,
                 flow_no: str = ''):
        self.customerAccount = customer_account
        self.time = time
        self.direction = direction
        self.name = name
        self.amount = amount
        self.balance = balance
        self.postscript = postscript
        self.sequence = sequence
        self.extension = extension if extension is not None else {}
        self.flowNo = flow_no

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __eq__(self, other):
        return self.is_same_trans(other)

    def is_same_trans(self, other):
        """是否为同一条流水，判断重复流水或最后一条流水使用"""
        if not isinstance(other, Transaction):
            return False
        # 当有流水号时，优先比对
        if self.flowNo and self.flowNo == other.flowNo:
            return True
        return (self.time == other.time and self.name == other.name
                and self.customerAccount == other.customerAccount and self.amount == other.amount
                and self.balance == other.balance and self.direction == other.direction
                and self.postscript == other.postscript)

    def to_dict(self, is_fen_amount=False):
        return {
            'time': format_datetime(self.time),
            'name': self.name,
            'customerAccount': self.customerAccount,
            'direction': self.direction,
            # 金额相关字段会有分单位值
            'amount': self.amount if is_fen_amount else amount_to_fen(self.amount),
            'balance': self.balance if is_fen_amount else amount_to_fen(self.balance),
            'flowNo': self.flowNo,
            'postscript': self.postscript,
            'sequence': self.sequence,
            'extension': self.extension if self.extension is not None else {},
        }

    @staticmethod
    def from_dict(trans_data: dict):
        # 使用 get 获取字段，可能不在 dict 中，最后一条流水返回字段不全
        return Transaction(customer_account=trans_data['customerAccount'], time=trans_data['time'],
                           direction=trans_data['direction'], name=trans_data['name'],
                           amount=trans_data['amount'], balance=trans_data['balance'],
                           postscript=trans_data['postscript'], sequence=trans_data['sequence'],
                           flow_no=trans_data.get('flowNo'), extension=trans_data.get('extension'))


# 机器人方法模型
class BotUtil:
    def __init__(self, cast_transfer: Callable = None, cast_transaction: Callable = None,
                 cast_start: Callable = None, cast_work: Callable = None,
                 cast_sms: Callable = None, make_bot: Callable = None, cast_work_flow: Callable = None):
        self.cast_work_flow = cast_work_flow
        self.cast_transfer = cast_transfer
        self.cast_transaction = cast_transaction
        self.cast_work = cast_work
        self.cast_start = cast_start
        self.cast_sms = cast_sms
        self.make_bot = make_bot


# 回单数据模型
class Receipt:
    def __init__(self, time: str = '', amount: int = 0, name: str = '', postscript: str = '',
                 customer_account: str = '', inner: bool = False, flow_no: str = '', sequence: int = 0,
                 need_format: str = 'json', bill_no: str = '', content: str = ''):
        self.time = time
        self.amount = amount
        self.name = name
        self.postscript = postscript
        self.customerAccount = customer_account
        self.inner = inner
        self.flowNo = flow_no
        self.billNo = bill_no
        self.sequence = sequence
        self.format = need_format
        self.content = content

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def need_image_format(self):
        """使用图片格式"""
        self.format = 'jpg'

    def generate_bill_no(self) -> str:
        """生成回单号，仅 `billNo` 无值时生成"""
        if not self.billNo:
            if self.time and self.name and self.customerAccount and self.amount:
                _ts = DateTimeHelper.to_str(self.time, '%Y%m%d%H%M%S')
                _original = f'{_ts}${self.name}${self.customerAccount}${self.amount}'
                # 最长 64 位，生成长度 47 = 14 + 1 + 32
                self.billNo = f'{_ts}_{StrHelper.md5(_original)}'
            else:
                raise Exception('先更新回单其他字段后，再调用此方法')
        return self.billNo

    def to_dict(self, is_fen_amount=False):
        # 生成回单号
        self.generate_bill_no()
        return {
            'time': format_datetime(self.time),
            'name': self.name,
            'customerAccount': self.customerAccount,
            # 金额相关字段会有分单位值
            'amount': self.amount if is_fen_amount else amount_to_fen(self.amount),
            'flowNo': self.flowNo,
            'inner': self.inner,
            'billNo': self.billNo,
            'postscript': self.postscript,
            'format': self.format,
            'content': self.content,
            'sequence': self.sequence,
        }


# 自动机机器人模型
class Bot:
    def __init__(self, serial_no: str = '', device: any = None, bank: any = None, account: Account = Account(),
                 last_trans: str = ''):
        self.serial_no = serial_no
        self.device = device
        self.bank = bank
        self.account = account  # Account
        self.last_trans = last_trans
        self.payment = False  # mode[receiving, payment]
        self.running = True
        self.pid = 0
        self.device_info = None

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


# 工作流打断方法返回值模型
class BreakRes:
    def __init__(self, is_break: bool = False, break_reason: str = ''):
        self.is_break = is_break
        self.break_reason = break_reason


# 制作抓流水类
class TransactionFactory(metaclass=abc.ABCMeta):
    @abstractmethod
    def get_transaction(self, last): pass

    @abstractmethod
    def check_detail_page(self): pass

    @abstractmethod
    def make_ele(self): pass
