import hashlib
import time
import re
from datetime import datetime
from typing import List, Callable, Union, Any


class RetryHelper:
    @staticmethod
    def retry_with_time(name: str, func: Callable, retry_limit: int = 60, interval: float = 0.5) -> [int, Any]:
        retry_time = 0
        loop_continue = retry_time <= retry_limit
        while loop_continue:
            result = func(retry_time=retry_time)
            if result:
                return retry_time, result
            retry_time += 1
            print(f'[{name}] 重试 {retry_time} 次')
            loop_continue = retry_time <= retry_limit
            if loop_continue and interval > 0:
                time.sleep(interval)

        return retry_time, None

    @staticmethod
    def retry(name: str, func: Callable, retry_limit: int = 60, interval: float = 0.5) -> [int, Any]:
        _, result = RetryHelper.retry_with_time(name, lambda **kwargs: func(), retry_limit, interval)
        return result

    @staticmethod
    def retry_with_callback(name: str, func: Callable, callback: [Callable, bool] = None,
                            retry_limit: int = 60, interval: float = 0.5) -> [int, Any]:
        retry_time = 0
        loop_continue = retry_time <= retry_limit
        while loop_continue:
            try:
                result = func(retry_time=retry_time)
                if result:
                    return retry_time, result
            except Exception as err:
                if callback is None:
                    raise err
                # 异常回调
                callback_result = callback(error=err)
                if not callback_result:
                    raise err

            retry_time += 1
            print(f'[{name}] 重试 {retry_time} 次')
            loop_continue = retry_time <= retry_limit
            if loop_continue and interval > 0:
                time.sleep(interval)

        return retry_time, None


class StrHelper:
    """字符串帮助类"""

    @staticmethod
    def contains(search, full) -> bool:
        return search in full

    @staticmethod
    def any_contains(searches: List[str], full) -> bool:
        """包含字符串列表任意一项"""
        for _s in searches:
            if _s in full:
                return True
        return False

    @staticmethod
    def trim_whitespace(text: str):
        return text.strip()

    @staticmethod
    def not_empty(text: str):
        return text and StrHelper.trim_whitespace(text) != ''

    @staticmethod
    def to_float(text: str):
        return float(text)

    @staticmethod
    def md5(text: str):
        _hash = hashlib.md5()
        _hash.update(text.encode('utf-8'))
        return _hash.hexdigest().upper()

    @staticmethod
    def is_match_card_num(card_mask: str, card_original: str):
        if not card_mask:
            return False

        re_str = ''
        is_star = False
        for ch in card_mask:
            if ch in ['*', ' ']:
                is_star = True
            else:
                if is_star:
                    re_str += r'\d*'
                    is_star = False
                re_str += ch

        return re.match(re_str, card_original) is not None


class NumericHelper:
    """数字相关帮助类"""

    @staticmethod
    def multiply_to_int(num: Union[float, str], multiplier: float) -> int:
        return int(float(num) * multiplier)

    @staticmethod
    def divide_to_float(num: Union[int, float], multiplier: float) -> float:
        return float(num) / multiplier


class DateTimeHelper:
    """日期帮助类"""

    @staticmethod
    def now_str(_format='%Y/%m/%d %H:%M:%S') -> str:
        return DateTimeHelper.to_str(datetime.now(), _format)

    @staticmethod
    def to_str(dt, _format='%Y/%m/%d %H:%M:%S') -> str:
        """格式化为 str 类型"""
        dt = DateTimeHelper.to_datetime(dt)
        return datetime.strftime(dt, _format)

    @staticmethod
    def to_datetime(_time, _format=None) -> datetime:
        """转换为 datetime 类型"""
        if isinstance(_time, datetime):
            return _time
        if isinstance(_time, str):
            if _format is None:
                # 默认识别两种格式
                _format = '%Y/%m/%d %H:%M:%S' if '/' in _time else '%Y-%m-%d %H:%M:%S'
            return datetime.strptime(_time, _format)

    @staticmethod
    def timestamp(_dt=None, seconds=True) -> int:
        """时间戳
        `_dt` 时间值，None 表示获取当前时间
        `seconds` True 为秒格式，False 为毫秒格式
        """
        now = DateTimeHelper.to_datetime(_dt) if _dt else datetime.now()
        return int(now.timestamp() if seconds else now.timestamp() * 10 ** 3)
