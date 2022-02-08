import base64
import datetime
import os
from abc import ABC

from server import settings
from server import api
from server.bot_factory import report_receipt
from server.bots.common.common_func import got_filter_transaction, start, stop, \
    check_report_transactions, time_compare, make_common_transaction
from server.bots.verification.verification_code import VerificationCode
from server.models import Transaction, TransactionFactory

package = 'com.chinamworld.main'
activity = 'com.ccb.start.MainActivity'
d = settings.bot.device


class CcbTransaction(TransactionFactory, ABC):
    def get_transaction(self, last):
        transaction_arr = '//android.widget.TextView'
        transaction = make_common_transaction(d, last, transaction_arr, "com.chinamworld.main:id/tv_transaction_type",
                                              self.check_detail_page, self.make_ele)
        return transaction

    def check_detail_page(self):
        if d(text="交易时间").exists(timeout=5):
            return True
        else:
            return False

    def make_ele(self):
        transaction_ele = Transaction()
        transaction_ele.customerAccount = d(text="卡号 ").right(
            resourceId="com.chinamworld.main:id/tv_account_card_number").get_text()
        transaction_ele.postscript = d(text="摘要").right(
            resourceId="com.chinamworld.main:id/tv_digest").get_text()
        transaction_ele.time = d(text="交易时间").right(
            resourceId="com.chinamworld.main:id/tv_trading_date").get_text().replace('/', '-')
        transaction_ele.name = ''
        if d(resourceId="com.chinamworld.main:id/tv_opposite_account").exists(timeout=5):
            if d(resourceId="com.chinamworld.main:id/tv_opposite_account").get_text() != '':
                transaction_ele.name = \
                    d(resourceId="com.chinamworld.main:id/tv_opposite_account").get_text().split(" ")[1]
        transaction_ele.extension = {}
        if d(resourceId="com.chinamworld.main:id/tv_remark").exists(timeout=5):
            if d(resourceId="com.chinamworld.main:id/tv_remark").get_text() != '':
                transaction_ele.extension = {"remark": d(resourceId="com.chinamworld.main:id/tv_remark").get_text()}
        transaction_ele.balance = d(text="余额").right(
            resourceId="com.chinamworld.main:id/tv_balance").get_text().replace(',', '')
        amount = d(resourceId="com.chinamworld.main:id/tv_trans_money").get_text().replace(',', '')
        transaction_ele.amount = amount[1:]
        if amount[0] == '+':
            transaction_ele.direction = 1
        else:
            transaction_ele.direction = 0
        d.press("back")
        return transaction_ele


def go_to_login():
    if d(resourceId="com.chinamworld.main:id/close").exists(timeout=5):
        d(resourceId="com.chinamworld.main:id/close").click()
    d(resourceId="com.chinamworld.main:id/home_drawer").click()
    d.sleep(1)
    d(resourceId="com.chinamworld.main:id/btn_login_new").click()
    d.wait_activity("com.ccb.framework.security.login.internal.view.LoginActivity", timeout=10)
    for l in settings.bot.account.login_pwd:
        if l.isupper():
            d.sleep(1)
            d(text="大小写转换").click()
            d.sleep(1)
            d(text=l).click()
            d.sleep(1)
            d(text="大小写转换").click()
            print("点击大写按钮内容：%s" % l)
        else:
            d.sleep(1)
            d(text=l).click()
            print("点击小写按钮内容：%s" % l)
    d.sleep(1)
    d(resourceId="com.chinamworld.main:id/btn_confirm").click()
    d.wait_activity("com.ccb.start.MainActivity", timeout=40)
    if d(resourceId="com.chinamworld.main:id/back").exists(timeout=10):
        d(resourceId="com.chinamworld.main:id/back").click()


def go_to_receipt():
    if d(resourceId="com.chinamworld.main:id/text_two").exists(timeout=30):
        d(resourceId="com.chinamworld.main:id/text_two").click()
        d.wait_activity("com.ccb.transfer.transferhomenew.view.TransferHomeActNew", timeout=20)
        d(text="转账记录").click()
        d.wait_activity("com.ccb.transfer.transferrecord.view.TransferRecordMainActivity", timeout=30)
        if d(className='android.widget.LinearLayout', index="0").exists(timeout=30):
            d(className='android.widget.LinearLayout', index="0").click()
            if d(text="交易时间").exists(timeout=20):
                time = d(text="交易时间").right(resourceId="com.chinamworld.main:id"
                                                       "/transfer_record_confirm_time").get_text(
                ).replace('/', '-')
                bill_no = d(text="凭证号").right(
                    resourceId="com.chinamworld.main:id/transfer_record_confirm_voucher").get_text()
                postscript = d(text="交易类型").right(
                    resourceId="com.chinamworld.main:id/transfer_record_confirm_type").get_text()
                amount = d(
                    resourceId="com.chinamworld.main:id/overseas_transfer_confirm_amount").get_text().replace("¥ ", "")
                customer_account = d(
                    resourceId="com.chinamworld.main:id/overseas_transfer_confirm_bankName").get_text()
                name = d(
                    resourceId="com.chinamworld.main:id/overseas_transfer_confrim_name").get_text()
                inner = len(postscript.split("他行")) <= 1
                transaction_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                # if settings.last_transferee.amount == "%.2f" % (
                #         float(amount)) and settings.last_transferee.holder == name and (
                #         settings.payment_time <= transaction_time < (
                #         settings.payment_time + datetime.timedelta(minutes=20))):
                settings.receipt.time = time
                settings.receipt.billNo = bill_no
                settings.receipt.postscript = postscript
                settings.receipt.amount = amount
                settings.receipt.customerAccount = customer_account
                settings.receipt.name = name
                settings.receipt.inner = inner
                if not os.path.exists('../payment_record'):
                    os.mkdir('../payment_record')
                d.screenshot('../payment_record/%s.jpg' % settings.receipt.billNo)
                with open('../payment_record/%s.jpg' % settings.receipt.billNo, "rb") as f:
                    settings.receipt.content = str(base64.b64encode(f.read()), "utf-8")
                    settings.receipt.format = 'jpg'
                    settings.receipt.imageFormat = 'jpg'
                    params = {'account_alias': settings.bot.account.alias}
                    report_receipt(params)
                settings.need_receipt_no = False
                d.sleep(1)
                d.press("back")
                d.sleep(1)
                d.press("back")
                d.sleep(1)
                d.press("back")
                return True
    return False


def go_to_transaction():
    if d(text="账户").exists(timeout=30):
        d(text="账户").click()
        d.wait_activity("com.ccb.myaccount.plusview.activity.MyAccountPlusMainActivity", timeout=30)
        if d(resourceId="com.chinamworld.main:id/my_account_detail").exists(timeout=30):
            d(resourceId="com.chinamworld.main:id/my_account_detail").click()
        else:
            if d(resourceId="com.chinamworld.main:id/detail").exists(timeout=10):
                d.sleep(1)
                d.press("back")
                return
        if d(resourceId="com.chinamworld.main:id/dlg_right_tv").exists(timeout=15):
            d(resourceId="com.chinamworld.main:id/dlg_right_tv").click()
            d.sleep(1)
            d.press("back")
            return
        d.wait_activity("com.ccb.framework.app.TitledActivity", timeout=20)
        if d(className='android.widget.RelativeLayout', index="1").exists(timeout=20):
            ccb_transaction = CcbTransaction()
            check_report_transactions(d, ccb_transaction)
            d.sleep(1)
            d.press("back")
            d.sleep(1)
            d.press("back")


def transfer():
    d(resourceId="com.chinamworld.main:id/menu_two").click()
    d.wait_activity("com.ccb.transfer.transferhomenew.view.TransferHomeActNew", timeout=20)
    d.xpath('//*[@resource-id="com.chinamworld.main:id/grid_function"]/android.widget.LinearLayout[1]').click()
    d.wait_activity("com.ccb.transfer.smarttransfer.view.SmartTransferMainAct", timeout=20)
    d(resourceId="com.chinamworld.main:id/tv_pay_account").click()
    d(text=(settings.bot.account.account[:4] + '***' + settings.bot.account.account[-4:])).click()
    d.sleep(3)
    d(resourceId="com.chinamworld.main:id/et_cash_name").click()
    d.send_keys(settings.transferee.holder, clear=True)
    d.sleep(3)
    d(resourceId="com.chinamworld.main:id/et_collection_account").click()
    d.send_keys(settings.transferee.account, clear=True)
    d.sleep(3)
    d(resourceId="com.chinamworld.main:id/iv_bank_arrow").click()
    d.sleep(3)
    d(resourceId="com.chinamworld.main:id/et_tran_amount").click()
    d.send_keys(settings.transferee.amount, clear=True)
    settings.log('press amount key: %s %s' % (settings.transferee.amount, datetime.datetime.now()),
                 settings.Level.COMMON)
    d.sleep(3)
    d(resourceId="com.android.systemui:id/back").click()
    d.sleep(3)
    d(resourceId="com.chinamworld.main:id/btn_right1").click()
    return


def input_sms(sms):
    if d(resourceId="com.chinamworld.main:id/dlg_right_tv").exists(timeout=5):
        d(resourceId="com.chinamworld.main:id/dlg_right_tv").click()
    if d(resourceId="com.chinamworld.main:id/et_code").exists(timeout=10):
        d(resourceId="com.chinamworld.main:id/et_code").click()
        d.send_keys(sms, clear=True)
        d.sleep(3)
        d(resourceId="com.chinamworld.main:id/btn_confirm").click()
        d.sleep(5)
        if d(resourceId="com.chinamworld.main:id/native_graph_iv").exists(timeout=10):
            d(resourceId="com.chinamworld.main:id/et_code").click()
            d.send_keys(settings.bot.account.payment_pwd, clear=True)
            d.sleep(5)
            d(resourceId="com.chinamworld.main:id/native_graph_iv").click()
            print("开始识别验证码了")
            info = d(resourceId="com.chinamworld.main:id/native_graph_iv").info
            x = info['bounds']['left']
            y = info['bounds']['top']
            img = "verification.jpg"
            d.screenshot(img)

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
                    d(resourceId="com.chinamworld.main:id/native_graph_et").click()
                    d.send_keys(code, clear=True)
                    if d(resourceId="com.chinamworld.main:id/native_graph_check_iv").exists(timeout=10):
                        d(resourceId="com.chinamworld.main:id/btn_confirm").click()
                        check_success()
                    else:
                        d(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        d.sleep(1)
                        d(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        d.sleep(1)
                        d(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        d.sleep(1)
                        d(resourceId="com.chinamworld.main:id/default_row_four_delete").click()
                        d.sleep(1)
                        put_code()
                else:
                    put_code()

            put_code()
        else:
            check_success()


def check_success():
    d.wait_activity("com.ccb.framework.security.base.successpage.CcbSuccessPageAct", timeout=20)
    if d(resourceId="com.chinamworld.main:id/tv_expand_text").exists(timeout=10):
        settings.payment_time = datetime.datetime.now()
        d.sleep(1)
        d(resourceId="com.chinamworld.main:id/title_right_view_container").click()
        api.transfer_result(settings.transferee.order_id, True)
        settings.log("payment: 付款成功 %s" % str(settings.transferee), settings.Level.RECEIPT_OF_PAYMENT)
        settings.need_receipt_no = True
        settings.last_transferee = settings.transferee
        settings.transferee = ''
        d.sleep(3)
        d.press("back")
    else:
        api.transfer_result(settings.transferee.order_id, False)
    return False


def do_work(task_name):
    if task_name == "start":
        start(d, package)
    if task_name == "stop":
        stop(d, package)
    if task_name == "go_to_transaction":
        go_to_transaction()
    if task_name == "go_to_login":
        go_to_login()
    if task_name == "transfer":
        transfer()
    if task_name == "go_to_receipt":
        go_to_receipt()
    if task_name == "go_home":
        d.press("home")
    if task_name == "back":
        d.press("back")
