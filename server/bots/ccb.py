import base64
import datetime
import os
import sys

sys.path.append("..")
import api
import settings
from bot_factory import report_transaction, report_receipt
from bots.verification.verification_code import VerificationCode
from models import Transferee

package = 'com.chinamworld.main'
activity = 'com.ccb.start.MainActivity'
self = settings.bot.device


def start():
    self.screen_on()
    settings.bot.pid = self.app_start(package)
    return self.app_wait(package)  # 等待应用运行, return pid(int)


def stop():
    self.app_stop(package)


def go_to_login():
    if self(resourceId="com.chinamworld.main:id/close").exists(timeout=5):
        self(resourceId="com.chinamworld.main:id/close").click()
    self(resourceId="com.chinamworld.main:id/home_drawer").click()
    self.sleep(1)
    self(resourceId="com.chinamworld.main:id/btn_login_new").click()
    self.wait_activity("com.ccb.framework.security.login.internal.view.LoginActivity", timeout=10)
    for l in settings.bot.account.login_pwd:
        if l.isupper():
            self.sleep(1)
            self(text="大小写转换").click()
            self.sleep(1)
            self(text=l).click()
            self.sleep(1)
            self(text="大小写转换").click()
            print("点击大写按钮内容：%s" % l)
        else:
            self.sleep(1)
            self(text=l).click()
            print("点击小写按钮内容：%s" % l)
    self.sleep(1)
    self(resourceId="com.chinamworld.main:id/btn_confirm").click()
    self.wait_activity("com.ccb.start.MainActivity", timeout=10)
    if self(resourceId="com.chinamworld.main:id/back").exists(timeout=10):
        self(resourceId="com.chinamworld.main:id/back").click()


def go_to_receipt():
    self(resourceId="com.chinamworld.main:id/text_two").click()
    self.wait_activity("com.ccb.transfer.transferhomenew.view.TransferHomeActNew", timeout=20)
    self(text="转账记录").click()
    self.wait_activity("com.ccb.transfer.transferrecord.view.TransferRecordMainActivity", timeout=30)
    if self(className='android.widget.LinearLayout', index="0").exists(timeout=40):
        self(className='android.widget.LinearLayout', index="0").click()
        if self(text="交易时间").exists(timeout=20):
            time = self(text="交易时间").right(resourceId="com.chinamworld.main:id"
                                                      "/transfer_record_confirm_time").get_text(
            ).replace('/', '-')
            bill_no = self(text="凭证号").right(
                resourceId="com.chinamworld.main:id/transfer_record_confirm_voucher").get_text()
            postscript = self(text="交易类型").right(
                resourceId="com.chinamworld.main:id/transfer_record_confirm_type").get_text()
            amount = self(
                resourceId="com.chinamworld.main:id/overseas_transfer_confirm_amount").get_text().replace("¥ ", "")
            customer_account = self(
                resourceId="com.chinamworld.main:id/overseas_transfer_confirm_bankName").get_text()
            name = self(
                resourceId="com.chinamworld.main:id/overseas_transfer_confrim_name").get_text()
            inner = len(postscript.split("他行")) <= 1
            transaction_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            if settings.last_transferee.amount == "%.2f" % (
                    float(amount)) and settings.last_transferee.holder == name and (
                    settings.payment_time <= transaction_time < (
                    settings.payment_time + datetime.timedelta(minutes=20))):
                settings.receipt.time = time
                settings.receipt.billNo = bill_no
                settings.receipt.postscript = postscript
                settings.receipt.amount = amount
                settings.receipt.customerAccount = customer_account
                settings.receipt.name = name
                settings.receipt.inner = inner
                if not os.path.exists('../payment_record'):
                    os.mkdir('../payment_record')
                self.screenshot('../payment_record/%s.jpg' % settings.receipt.billNo)
                with open('../payment_record/%s.jpg' % settings.receipt.billNo, "rb") as f:
                    settings.receipt.content = str(base64.b64encode(f.read()), "utf-8")
                    settings.receipt.format = 'jpg'
                    settings.receipt.imageFormat = 'jpg'
                    params = {'account_alias': settings.bot.account.alias}
                    report_receipt(params)
            settings.need_receipt_no = False
            self.sleep(1)
            self.press("back")
            self.sleep(1)
            self.press("back")
            self.sleep(1)
            self.press("back")


def go_to_transaction():
    self(resourceId="com.chinamworld.main:id/text_item", text="账户").click()
    self.wait_activity("com.ccb.myaccount.plusview.activity.MyAccountPlusMainActivity", timeout=30)
    if self(resourceId="com.chinamworld.main:id/my_account_detail").exists(timeout=40):
        self(resourceId="com.chinamworld.main:id/my_account_detail").click()
    if self(resourceId="com.chinamworld.main:id/dlg_right_tv").exists(timeout=15):
        self(resourceId="com.chinamworld.main:id/dlg_right_tv").click()
        self.sleep(1)
        self.press("back")
        return
    self.wait_activity("com.ccb.framework.app.TitledActivity", timeout=20)
    if self(className='android.widget.RelativeLayout', index="1").exists(timeout=20):
        settings.check_transaction = True
        while settings.check_transaction:
            make_transaction()
        print('settings.total_transaction: %s' % settings.total_transaction)
        if len(settings.total_transaction) > 0:
            params = {'account_alias': settings.bot.account.alias, 'balance': settings.total_transaction[0]['balance'],
                      'transactions': settings.total_transaction}
            report_transaction(params)
            settings.total_transaction = []
        self.sleep(1)
        self.press("back")
        self.sleep(1)
        self.press("back")


def make_transaction():
    settings.got_transaction = get_transaction()
    if settings.middle_break:
        settings.middle_break = False
        return
    if settings.last_transferee != [] and settings.last_transaction_list == settings.got_transaction:
        got_filter_transaction()
    else:
        settings.last_transaction_list = settings.got_transaction
        for ele in settings.got_transaction:
            settings.temp_transaction.append(ele)
        self.sleep(1)
        self.swipe_ext("up", scale=0.4)
        self.sleep(1)


def got_filter_transaction():
    for item in settings.temp_transaction:
        if item != {} and not item in settings.total_transaction:
            settings.total_transaction.append(item)
    settings.temp_transaction = []
    settings.got_transaction = []
    settings.last_transaction_list = []
    settings.check_transaction = False
    return


def get_transaction():
    transaction = []
    a = 0
    last = api.last_transaction(settings.bot.account.alias)
    last_time = last['data']['time']
    for elem in self.xpath('//android.widget.TextView').all():
        if elem.attrib['resource-id'] == "com.chinamworld.main:id/tv_transaction_type":
            transaction.append({})
            elem.click()
            if self(text="交易时间").exists(timeout=5):
                transaction[a]['customerAccount'] = self(text="卡号 ").right(
                    resourceId="com.chinamworld.main:id/tv_account_card_number").get_text()
                transaction[a]['postscript'] = self(text="摘要").right(
                    resourceId="com.chinamworld.main:id/tv_digest").get_text()
                transaction[a]['time'] = self(text="交易时间").right(
                    resourceId="com.chinamworld.main:id/tv_trading_date").get_text().replace('/', '-')
                transaction[a]['name'] = self(text="对方账户").right(
                    resourceId="com.chinamworld.main:id/tv_opposite_account").get_text().split(" ")[1]
                transaction[a]['remark'] = self(text="交易地点/附言").right(
                    resourceId="com.chinamworld.main:id/tv_remark").get_text()
                transaction[a]['balance'] = self(text="余额").right(
                    resourceId="com.chinamworld.main:id/tv_balance").get_text()
                amount = self(resourceId="com.chinamworld.main:id/tv_trans_money").get_text()
                transaction[a]['amount'] = amount[1:]
                if amount[0] == '+':
                    transaction[a]['direction'] = 1
                else:
                    transaction[a]['direction'] = 0
                self.sleep(1)
                self.press("back")
                print('ele time: %s last time: %s ele amount: %s last amount: %s' % (
                    transaction[a]['time'], last_time, "%.2f" % (float(transaction[a]['amount']) * 100),
                    "%.2f" % (float(last['data']['amount']))))
                if transaction[a]['time'] == last_time and "%.2f" % (
                        float(transaction[a]['amount']) * 100) == "%.2f" % (
                        float(last['data']['amount'])):
                    del transaction[a]
                    for ele in transaction:
                        settings.temp_transaction.append(ele)
                    got_filter_transaction()
                    settings.middle_break = True
                    return transaction
                else:
                    a += 1

    last_index = len(transaction) - 1
    if transaction[last_index] == {}:
        del transaction[last_index]
    print('get_transaction: %s' % transaction)
    return transaction


def transfer():
    self(resourceId="com.chinamworld.main:id/menu_two").click()
    self.wait_activity("com.ccb.transfer.transferhomenew.view.TransferHomeActNew", timeout=20)
    self.xpath('//*[@resource-id="com.chinamworld.main:id/grid_function"]/android.widget.LinearLayout[1]').click()
    self.wait_activity("com.ccb.transfer.smarttransfer.view.SmartTransferMainAct", timeout=20)
    self(resourceId="com.chinamworld.main:id/tv_pay_account").click()
    self(text=(settings.bot.account.account[:4] + '***' + settings.bot.account.account[-4:])).click()
    self.sleep(3)
    self(resourceId="com.chinamworld.main:id/et_cash_name").click()
    self.send_keys(settings.transferee.holder, clear=True)
    self.sleep(3)
    self(resourceId="com.chinamworld.main:id/et_collection_account").click()
    self.send_keys(settings.transferee.account, clear=True)
    self.sleep(3)
    self(resourceId="com.chinamworld.main:id/iv_bank_arrow").click()
    self.sleep(3)
    self(resourceId="com.chinamworld.main:id/et_tran_amount").click()
    self.send_keys(settings.transferee.amount, clear=True)
    self.sleep(3)
    self(resourceId="com.android.systemui:id/back").click()
    self.sleep(3)
    self(resourceId="com.chinamworld.main:id/btn_right1").click()
    return


def input_sms(sms):
    if self(resourceId="com.chinamworld.main:id/dlg_right_tv").exists(timeout=5):
        self(resourceId="com.chinamworld.main:id/dlg_right_tv").click()
    if self(resourceId="com.chinamworld.main:id/et_code").exists(timeout=10):
        self(resourceId="com.chinamworld.main:id/et_code").click()
        self.send_keys(sms, clear=True)
        self.sleep(3)
        self(resourceId="com.chinamworld.main:id/btn_confirm").click()
        self.sleep(5)
        if self(resourceId="com.chinamworld.main:id/native_graph_iv").exists(timeout=10):
            self(resourceId="com.chinamworld.main:id/et_code").click()
            self.send_keys(settings.bot.account.payment_pwd, clear=True)
            self.sleep(5)
            self(resourceId="com.chinamworld.main:id/native_graph_iv").click()
            print("开始识别验证码了")
            info = self(resourceId="com.chinamworld.main:id/native_graph_iv").info
            x = info['bounds']['left']
            y = info['bounds']['top']
            img = "verification.jpg"
            self.screenshot(img)

            def get_code():
                vc = VerificationCode(x, y, 313, 165, img, settings.bot.bank, 4)
                if not settings.read_img_lock:
                    settings.read_img_lock = True
                    return vc.image_str(True)
                else:
                    return None

            def put_code():
                code = get_code()
                if code is None:
                    return
                if len(code) == 4:
                    self(resourceId="com.chinamworld.main:id/native_graph_et").click()
                    self.send_keys(code, clear=True)
                    if self(resourceId="com.chinamworld.main:id/native_graph_check_iv").exists(timeout=10):
                        self(resourceId="com.chinamworld.main:id/btn_confirm").click()
                        check_success()
                    else:
                        self(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        self.sleep(1)
                        self(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        self.sleep(1)
                        self(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        self.sleep(1)
                        self(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        self.sleep(1)
                        put_code()
                else:
                    put_code()

            put_code()
        else:
            check_success()


def check_success():
    self.wait_activity("com.ccb.framework.security.base.successpage.CcbSuccessPageAct", timeout=20)
    if self(resourceId="com.chinamworld.main:id/tv_expand_text").exists(timeout=10):
        if not os.path.exists('payment_record'):
            os.mkdir('payment_record')
        self.screenshot('payment_record/%s.jpg' % datetime.datetime.now())
        self.sleep(1)
        self(resourceId="com.chinamworld.main:id/title_right_view_container").click()
        api.transfer_result(settings.transferee.order_id, True)
        settings.log("payment: 付款成功 %s" % str(settings.transferee), settings.Level.RECEIPT_OF_PAYMENT)
        settings.need_receipt_no = True
        settings.last_transferee = settings.transferee
        settings.transferee = ''
        self.sleep(3)
        self.press("back")
    else:
        api.transfer_result(settings.transferee.order_id, False)
    return False


def do_work(task_name):
    if task_name == "start":
        start()
    if task_name == "go_to_transaction":
        go_to_transaction()
    if task_name == "go_to_login":
        go_to_login()
    if task_name == "transfer":
        transfer()
    if task_name == "go_to_receipt":
        go_to_receipt()
    if task_name == "go_home":
        self.press("home")
    if task_name == "back":
        self.press("back")
