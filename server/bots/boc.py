import base64
import datetime
import os
import sys

sys.path.append("..")
import api
import settings
from bots.verification.verification_code import VerificationCode

package = 'com.chinamworld.bocmbci'
activity = 'com.boc.bocsoft.mobile.bocmobile.buss.system.main.ui.MainActivity'
self = settings.bot.device


def start():
    self.screen_on()
    settings.bot.pid = self.app_start(package)
    return self.app_wait(package)  # 等待应用运行, return pid(int)


def stop():
    self.sleep(1)
    self.app_stop(package)
    self.app_stop('com.termux')


def input_pwd():
    original = {
        "0": [0.056, 0.681],
        "1": [0.148, 0.679],
        "2": [0.254, 0.68],
        "3": [0.348, 0.682],
        "4": [0.446, 0.681],
        "5": [0.542, 0.68],
        "6": [0.644, 0.677],
        "7": [0.746, 0.679],
        "8": [0.84, 0.68],
        "9": [0.948, 0.683],
    }
    switcher = {
        "0": [0.056, 0.681],
        "1": [0.148, 0.679],
        "2": [0.254, 0.68],
        "3": [0.348, 0.682],
        "4": [0.446, 0.681],
        "5": [0.542, 0.68],
        "6": [0.644, 0.677],
        "7": [0.746, 0.679],
        "8": [0.84, 0.68],
        "9": [0.948, 0.683],
        "q": [0.06, 0.754],
        "w": [0.156, 0.754],
        "e": [0.252, 0.754],
        "r": [0.342, 0.75],
        "t": [0.452, 0.748],
        "y": [0.548, 0.754],
        "u": [0.648, 0.754],
        "i": [0.744, 0.748],
        "o": [0.844, 0.753],
        "p": [0.94, 0.753],
        "ca": [0.052, 0.822],
        "a": [0.158, 0.822],
        "s": [0.25, 0.821],
        "d": [0.344, 0.82],
        "f": [0.442, 0.82],
        "g": [0.544, 0.824],
        "h": [0.646, 0.824],
        "j": [0.742, 0.821],
        "k": [0.844, 0.821],
        "l": [0.942, 0.821],
        "z": [0.204, 0.896],
        "x": [0.294, 0.898],
        "c": [0.402, 0.9],
        "v": [0.496, 0.896],
        "b": [0.598, 0.897],
        "n": [0.694, 0.898],
        "m": [0.796, 0.897],
    }

    def get_pwd():
        arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self(resourceId="com.chinamworld.bocmbci:id/loginPasswordSipBox").click()
        self.sleep(5)
        start_info = self.xpath('//android.widget.LinearLayout[1]/android.view.View[1]').info
        print(start_info)
        x = 0
        y = 1448
        width = x + int(start_info['bounds']['right'])
        height = 135
        img = "verification.jpg"
        self.sleep(2)
        self.screenshot(img)
        vc = VerificationCode(x, y, width, height, img, 'boc', 10)
        pwd_code = vc.image_str()
        for letter in pwd_code:
            if letter.isdigit() and int(letter) in arr:
                arr.remove(int(letter))
        print("未识别到字符：%s" % arr)
        print("已识别到字符：%s" % pwd_code)
        if len(arr) != 0:
            pwd_code = get_pwd()
        return pwd_code

    code = get_pwd()
    print(code)
    if code != "" or code is not None or len(code) == 10:
        num = list(code)
        j = 0
        for i in num:
            switcher[i] = original[str(j)]
            print("已识别数字 = %s and 撞键盘= %s and original[str(j)] = %s" % (i, j, original[str(j)]))
            j += 1
        print(switcher)
        for l in settings.bot.account.login_pwd:
            if l.isupper():
                btn_xy = switcher.get(l.lower())
                ca_xy = switcher.get("ca")
                self.sleep(1)
                self.click(ca_xy[0], ca_xy[1])
                self.sleep(1)
                self.click(btn_xy[0], btn_xy[1])
                self.sleep(1)
                self.click(ca_xy[0], ca_xy[1])
                print("点击大写按钮坐标：%s" % btn_xy)
                print("点击大写按钮内容：%s" % l)
            else:
                btn_xy = switcher.get(l)
                self.sleep(1)
                self.click(btn_xy[0], btn_xy[1])
                print("点击小写按钮坐标：%s" % btn_xy)
                print("点击小写按钮内容：%s" % l)
        self.sleep(1)
        self(resourceId="com.chinamworld.bocmbci:id/loginSubmitBtn").click()
        self.sleep(1)
        while self(text="暂不体验").exists(timeout=3):
            self(text="暂不体验").click()


def go_to_transaction():
    self(resourceId="com.chinamworld.bocmbci:id/tv_item", text="账户管理").click()
    self.wait_activity("com.boc.bocsoft.mobile.bocmobile.buss.account.Module.AccountActivity", timeout=10)
    self.sleep(3)
    self(resourceId="com.chinamworld.bocmbci:id/btn_left").click()


def transfer():
    if self(text="转账").exists(timeout=20):
        self(text="转账").click()
        self.wait_activity("com.boc.bocsoft.mobile.bocmobile.buss.transfer.common.activity.TransferActivity",
                           timeout=10)
        self(text="账号转账").click()
        if self(resourceId="com.chinamworld.bocmbci:id/txt_money_title").exists(timeout=60):
            self.xpath(
                '//*[@resource-id="com.chinamworld.bocmbci:id/transfer_payeracc"]/android.widget.LinearLayout['
                '1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]').click()
            get_account = self(resourceId="com.chinamworld.bocmbci:id/tv_number").get_text()
            get_account = get_account[-4:-1]
            account = settings.bot.account.account[-4:-1]
            if get_account == account:
                self(resourceId="com.chinamworld.bocmbci:id/tv_number").click()
                if self(resourceId="com.chinamworld.bocmbci:id/txt_money_title").exists(timeout=10):
                    input_amount()
                    self(resourceId="com.chinamworld.bocmbci:id/clear_edit_context").click()
                    self.send_keys(settings.transferee.account, clear=True)
                    self.sleep(3)
                    self(resourceId="com.chinamworld.bocmbci:id/trans_remit_payeename").click()
                    self.send_keys(settings.transferee.holder, clear=True)
                    self.sleep(3)
                    if self(resourceId="com.chinamworld.bocmbci:id/choice_data_arrow", description="点击更换收款银行").exists(
                            timeout=5):
                        self.sleep(2)
                        self(resourceId="com.chinamworld.bocmbci:id/choice_data_arrow", description="点击更换收款银行").click()
                        self.sleep(2)
                        self.swipe_ext("up", scale=0.8)
                        self.sleep(2)
                    submit_btn()


def input_sms(sms):
    sms_switcher = {
        "0": [0.495, 0.895],
        "1": [0.168, 0.683],
        "2": [0.488, 0.677],
        "3": [0.822, 0.678],
        "4": [0.165, 0.751],
        "5": [0.497, 0.75],
        "6": [0.82, 0.752],
        "7": [0.168, 0.823],
        "8": [0.493, 0.824],
        "9": [0.822, 0.819],
    }
    for i in sms:
        btn_xy = sms_switcher.get(i)
        self.click(btn_xy[0], btn_xy[1])
        self.sleep(1)
    settings.payment_time = datetime.datetime.now()
    settings.log("cast_sms: %s payment_time: %s" % (sms, settings.payment_time))
    if self(resourceId="com.chinamworld.bocmbci:id/tv_detail").exists(timeout=20):
        api.transfer_result(settings.transferee.order_id, True)
        settings.log("payment: 付款成功 %s" % str(settings.transferee), settings.Level.RECEIPT_OF_PAYMENT)
        settings.need_receipt_no = True
        settings.need_receipt = True
        settings.last_transferee = settings.transferee
        settings.transferee = ''
        self.sleep(5)
        self(resourceId="com.chinamworld.bocmbci:id/btn_home").click()
    else:
        api.transfer_result(settings.transferee.order_id, False)
    return False


def submit_btn():
    self(resourceId="com.chinamworld.bocmbci:id/trans_remit_next").click()
    if self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="安全工具").exists(timeout=20):
        self(resourceId="com.chinamworld.bocmbci:id/tv_btn").click()
        self.sleep(2)
        self.xpath('//*[@resource-id="com.chinamworld.bocmbci:id/list_view"]/android.widget.RelativeLayout[1]').click()
        self(resourceId="com.chinamworld.bocmbci:id/btn_ok").click()


def input_amount():
    self.xpath(
        '//*[@resource-id="com.chinamworld.bocmbci:id/trans_remit_money"]/android.widget.LinearLayout['
        '1]/android.widget.LinearLayout[1]').click()
    self.sleep(3)
    num_keyboard = [
        "com.chinamworld.bocmbci:id/pay_keyboard_zero",
        "com.chinamworld.bocmbci:id/pay_keyboard_one",
        "com.chinamworld.bocmbci:id/pay_keyboard_two",
        "com.chinamworld.bocmbci:id/pay_keyboard_three",
        "com.chinamworld.bocmbci:id/pay_keyboard_four",
        "com.chinamworld.bocmbci:id/pay_keyboard_five",
        "com.chinamworld.bocmbci:id/pay_keyboard_sex",
        "com.chinamworld.bocmbci:id/pay_keyboard_seven",
        "com.chinamworld.bocmbci:id/pay_keyboard_eight",
        "com.chinamworld.bocmbci:id/pay_keyboard_nine",
        "com.chinamworld.bocmbci:id/pay_keyboard_point",
    ]
    for amount_num in settings.transferee.amount:
        self.sleep(1)
        if amount_num == "0":
            self(resourceId=num_keyboard[0]).click()
        if amount_num == "1":
            self(resourceId=num_keyboard[1]).click()
        if amount_num == "2":
            self(resourceId=num_keyboard[2]).click()
        if amount_num == "3":
            self(resourceId=num_keyboard[3]).click()
        if amount_num == "4":
            self(resourceId=num_keyboard[4]).click()
        if amount_num == "5":
            self(resourceId=num_keyboard[5]).click()
        if amount_num == "6":
            self(resourceId=num_keyboard[6]).click()
        if amount_num == "7":
            self(resourceId=num_keyboard[7]).click()
        if amount_num == "8":
            self(resourceId=num_keyboard[8]).click()
        if amount_num == "9":
            self(resourceId=num_keyboard[9]).click()
        if amount_num == ".":
            self(resourceId=num_keyboard[10]).click()
        settings.log('press amount key: %s' % amount_num, settings.Level.COMMON)
    self(resourceId="com.android.systemui:id/back").click()
    self.sleep(3)


def go_to_receipt():
    if self(text="转账").exists(timeout=20):
        self(resourceId="com.chinamworld.bocmbci:id/tv_item", text="转账").click()
        get_receipt()


def get_receipt():
    if self(resourceId="com.chinamworld.bocmbci:id/tv_trans_record").exists(timeout=20):
        self(resourceId="com.chinamworld.bocmbci:id/tv_trans_record").click()
        try_web()


def money_format(amount):
    res = format(float(amount), ",")
    if len(res.split('.')[1]) < 2:
        res = res + '0'
    return res


def try_web():
    if self(text="服务器开小差了，请稍后再试").exists(timeout=10):
        self.press("back")
        get_receipt()
    else:
        if self(text="近3个月查询结果").exists(timeout=10):
            if self(text="%s人民币元%s" % (
                    settings.last_transferee.holder, money_format(settings.last_transferee.amount))).exists(timeout=10):
                self(text="%s人民币元%s" % (
                    settings.last_transferee.holder, money_format(settings.last_transferee.amount))).click()
                if self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="交易序号").exists(timeout=10):
                    self.sleep(3)
                    flow_no = self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="交易序号").right(
                        resourceId="com.chinamworld.bocmbci:id/tv_value").get_text()
                    if not os.path.exists('../payment_record'):
                        os.mkdir('../payment_record')
                    self.screenshot('../payment_record/%s.jpg' % flow_no)
                    with open('../payment_record/%s.jpg' % flow_no, "rb") as f:
                        settings.receipt_no.content = str(base64.b64encode(f.read()), "utf-8")
                        settings.receipt_no.format = 'jpg'
                        settings.receipt_no.imageFormat = 'jpg'
                    self.sleep(1)
                    if self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="人行报文号").exists(timeout=3):
                        bill_no = self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="人行报文号").right(
                            resourceId="com.chinamworld.bocmbci:id/tv_value").get_text()
                    else:
                        bill_no = flow_no
                    name = self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="收款人名称").right(
                        resourceId="com.chinamworld.bocmbci:id/tv_value").get_text()
                    account = self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="收款账号").right(
                        resourceId="com.chinamworld.bocmbci:id/tv_value").get_text()
                    time = self(resourceId="com.chinamworld.bocmbci:id/tv_name", text="交易日期").right(
                        resourceId="com.chinamworld.bocmbci:id/tv_value").get_text()
                    amount = self(resourceId="com.chinamworld.bocmbci:id/tv_sum").get_text()
                    settings.receipt_no.time = time
                    settings.receipt_no.name = name
                    settings.receipt_no.customerAccount = account
                    settings.receipt_no.flowNo = flow_no
                    settings.receipt_no.billNo = bill_no
                    settings.receipt_no.amount = amount.replace(",", '')
                    settings.log('bill_no: %s account: %s name: %s flow_no: %s time: %s amount: %s' % (
                        bill_no, account, name, flow_no, time, amount), settings.Level.COMMON)
                    settings.need_receipt_no = False
                    self.press("back")
                    self.sleep(1)
                    self.press("back")
                    self.sleep(1)
                    self.press("back")
                    self.sleep(1)
                else:
                    self.press("back")
                    self.press("back")
                    get_receipt()
            else:
                if self(text="%s交易失败人民币元%s" % (
                        settings.last_transferee.holder, money_format(settings.last_transferee.amount))).exists(
                    timeout=10):
                    settings.need_receipt_no = False
                    settings.need_receipt = False
                    self.press("back")
                    self.sleep(1)
                    self.press("back")
                    self.sleep(1)
                    return False
                self.press("back")
                get_receipt()
        else:
            self.press("back")
            get_receipt()


def do_work(task_name):
    if task_name == "stop":
        stop()
    if task_name == "input_pwd":
        input_pwd()
    if task_name == "start":
        start()
    if task_name == "go_to_transaction":
        go_to_transaction()
    if task_name == "go_home":
        self.press("home")
    if task_name == "back":
        self.press("back")
    if task_name == "transfer":
        transfer()
    if task_name == 'go_to_receipt':
        go_to_receipt()
