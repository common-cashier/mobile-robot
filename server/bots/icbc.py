import base64
import os
import time
from abc import ABC

from server.bots.common.common_func import start, check_report_transactions, stop, \
    make_common_transaction, get_file_list
from server.models import Transaction, TransactionFactory
import server.settings as settings
from server import api

package = 'com.icbc'
activity = 'com.icbc.activity.main.MainActivity'
d = settings.bot.device


class IcbcTransaction(TransactionFactory, ABC):
    def get_transaction(self, last):
        transaction_arr = '//android.widget.TextView'
        print('last: %s' % last)
        print('transaction_arr: %s' % transaction_arr)
        transaction = make_common_transaction(d, last, transaction_arr, "com.icbc:id/tv_titleValue",
                                              self.check_detail_page, self.make_ele)
        return transaction

    def check_detail_page(self):
        print('start check_detail_page')
        if d.wait_activity("com.icbc.mydetail.MyDetailRemarkActivity"):
            print('start check_detail_page activity')
            if d(resourceId="com.icbc:id/tv_look_mydetail").exists(timeout=30):
                print('start check_detail_page detail_btn')
                return True
        else:
            return False

    def make_ele(self):
        transaction_ele = Transaction()
        print('start make transaction')
        amount = d(resourceId="com.icbc:id/tv_account_mydetail").get_text(timeout=20)
        print('click transaction details')
        d(resourceId="com.icbc:id/tv_look_mydetail").click()
        if amount[0] == '+':
            transaction_ele.direction = 1
        else:
            transaction_ele.direction = 0
        transaction_ele.amount = amount[1:]
        transaction_ele.balance = d(resourceId="com.icbc:id/tv_account_balance").get_text()[3:]
        print('got base details')
        if d(text="记账金额").exists(timeout=30):
            if d(text="对方账户").exists(timeout=5):
                transaction_ele.customerAccount = d(text="对方账户").right(
                    resourceId="com.icbc:id/tv_right").get_text()
                transaction_ele.name = d(text="对方户名").right(
                    resourceId="com.icbc:id/tv_right").get_text()
            print('getting details')
            transaction_ele.time = d(text="交易时间").right(
                resourceId="com.icbc:id/tv_right").get_text()
            transaction_ele.postscript = d(text="业务摘要").right(
                resourceId="com.icbc:id/tv_right").get_text()
        print('complete details')
        d.press("back")
        return transaction_ele


def go_to_login():
    gesture_pwd = {
        1: (0.211, 0.441),
        2: (0.5, 0.44),
        3: (0.791, 0.44),
        4: (0.219, 0.582),
        5: (0.5, 0.579),
        6: (0.786, 0.576),
        7: (0.211, 0.72),
        8: (0.5, 0.715),
        9: (0.788, 0.715)
    }

    customer_pwd = list(settings.bot.account.key_pwd)
    print(customer_pwd)
    if d.wait_activity("com.icbc.activity.main.MainActivity", timeout=30):
        d(resourceId="com.icbc:id/tv_login").click()
        if d.wait_activity("com.icbc.component.gesture.NoPerceptionGestureActivity", timeout=30):
            point_group = []
            for i in customer_pwd:
                print('swipe_start:%s' % i)
                point_group.append(gesture_pwd.get(int(i)))
            d.swipe_points(point_group, 0.2)


def go_to_receipt():
    d(resourceId="researchRemitEtransHistory").click()
    if d.wait_activity("com.icbc.activity.remit.QueryRemitListActivityZJ", timeout=30):
        k = 1
        while k < 4:
            account_obj = d.xpath(
                '//android.widget.ListView/android.widget.LinearLayout[%s]/android.widget.LinearLayout['
                '1]/android.widget.RelativeLayout[2]/android.widget.TextView[3]' % k)
            account = account_obj.get_text()
            amount = d.xpath(
                '//android.widget.ListView/android.widget.LinearLayout[%s]/android.widget.LinearLayout['
                '1]/android.widget.RelativeLayout[2]/android.widget.TextView[2]' % k).get_text()
            short_account = settings.transferee.account[-4:]
            print('抓取回单account：' + account[-4:] + ' 实际account:' + short_account + ' 转账：' + amount[
                                                                                           1:] + " 实际转账：" + "%.2f" % float(
                settings.transferee.amount) + " 账号是否相等：" + str(account[-4:] == short_account) + " 金额是否相等：" + str(
                amount[1:] == "%.2f" % float(settings.transferee.amount)))
            if account[-4:] == short_account and amount[1:] == "%.2f" % float(settings.transferee.amount):
                print("已匹配回单的账号和余额")
                account_obj.click()
                if d(text="交易日期").exists(timeout=20):
                    settings.receipt.time = d(text="交易日期").right(resourceId="com.icbc:id/tv_titleValue").get_text(timeout=20)
                    settings.receipt.name = d(text="收款人").right(resourceId="com.icbc:id/tv_titleValue").get_text()
                    settings.receipt.customerAccount = d(text="收款账号").right(resourceId="com.icbc:id/tv_titleValue").get_text()
                    settings.receipt.amount = d(text="金额").right(resourceId="com.icbc:id/tv_titleValue").get_text()[:-1]
                    settings.receipt.sequence = 0
                    settings.receipt.billNo = settings.receipt.generate_bill_no()
                    if d(resourceId="com.icbc:id/btn_queryRemit", text="电子回单").exists(20):
                        d(resourceId="com.icbc:id/btn_queryRemit", text="电子回单").click()
                        while d(resourceId="com.icbc:id/tv_loading_tip").exists(2):
                            continue
                        if d(text="下载到相册").exists(timeout=20):
                            d(text="下载到相册").click()
                            if d(resourceId="com.icbc:id/adp_button2").exists(timeout=20):
                                d(resourceId="com.icbc:id/adp_button2").click()
                                real_path = "/sdcard/ICBC/picture/"
                                if os.path.exists(real_path):
                                    pic_list = get_file_list(real_path)
                                    pic_path = real_path + pic_list[-1]
                                    with open(pic_path, "rb") as f:
                                        settings.receipt.content = str(base64.b64encode(f.read()), "utf-8")
                                        settings.receipt.format = 'png'
                                        settings.receipt.imageFormat = 'png'
                                        params = {'account_alias': settings.bot.account.alias}
                                        api.receipt(params['account_alias'], [settings.receipt.to_dict()])
                    k += 4
            k += 1


def go_to_transaction():
    if d.wait_activity("com.icbc.activity.main.MainActivity", timeout=30):
        d(resourceId="com.icbc:id/tv_favorite_kingkong_title_2").click()
        if d.wait_activity("com.icbc.myaccountsixth.MyAccountSixthActivity", timeout=30):
            d.xpath('//*[@resource-id="com.icbc:id/ll_card_num_view"]/android.widget.LinearLayout[2]').click()
            if d(resourceId="com.icbc:id/tv_account_menu_name", text="查询明细").exists(timeout=30):
                d(resourceId="com.icbc:id/tv_account_menu_name", text="查询明细").click()
                if d.wait_activity("com.icbc.activity.remit.QueryDetailActivity", timeout=30):
                    d(resourceId="com.icbc:id/head_img_right").click()
                    icbc_transaction = IcbcTransaction()
                    check_report_transactions(d, icbc_transaction)
                    d.sleep(1)
                    d.press("back")
                    d.sleep(1)
                    d.press("back")
                    d.sleep(1)
                    d.press("back")
                    d.sleep(1)
                    d.press("back")


def transfer():
    click_pwd = {
        0: [0.5, 0.897],
        1: [0.166, 0.68],
        2: [0.502, 0.682],
        3: [0.83, 0.68],
        4: [0.169, 0.754],
        5: [0.5, 0.755],
        6: [0.833, 0.755],
        7: [0.166, 0.827],
        8: [0.502, 0.83],
        9: [0.833, 0.827]
    }
    if d.wait_activity("com.icbc.activity.main.MainActivity", timeout=30):
        d(resourceId="com.icbc:id/icon_txt", text="转账汇款").click()
        if d(resourceId="nav_title").exists(timeout=40):
            if d(resourceId="nav_title").get_text() == '转账汇款':
                d.xpath('//*[@text="境内汇款 免费"]/android.view.View[1]/android.view.View[1]').click()
                if d.wait_activity("com.icbc.activity.web.ICBCWebView", timeout=30):
                    if d(resourceId="nav_title").exists(timeout=40):
                        if d(resourceId="nav_title").get_text() == '境内汇款':
                            d.xpath('//*[@resource-id="accountacctCell"]/android.view.View[2]').set_text(
                                settings.transferee.account)
                            d.xpath(
                                '//*[@resource-id="scroller"]/android.view.View[3]/android.view.View['
                                '4]/android.view.View[2] '
                            ).set_text(str(settings.transferee.amount))
                            d.xpath('//*[@resource-id="accountnameCell"]/android.view.View[2]').set_text(
                                settings.transferee.holder)
                            d.click(0.205, 0.742)
                            d.sleep(2)
                            d.click(0.5, 0.635)
                            if d(resourceId="com.icbc:id/verifyControlDialogTitle2").exists(timeout=20):
                                for i in settings.bot.account.payment_pwd:
                                    print("i : %s" % i)
                                    print("i : %s" % type(i))
                                    btn_xy = click_pwd.get(int(i))
                                    d.click(btn_xy[0], btn_xy[1])
                                if d(text="款项已经汇入收款人账户。").exists(timeout=40):
                                    go_to_receipt()
                                    time.sleep(1)
                                    d.press('back')
                                    time.sleep(1)
                                    d.press('back')
                                    time.sleep(1)
                                    d.press('back')
                                    time.sleep(1)
                                    d.press('back')
                                    time.sleep(1)
                                    d.press('back')
                                    time.sleep(1)
                                    go_to_transaction()


def input_sms(sms):
    return False


def is_login():
    print("do_login: check")
    if d.wait_activity("com.icbc.activity.main.MainActivity", timeout=30):
        print("do_login: start")
        if d(resourceId="com.icbc:id/tv_login").exists(timeout=5):
            print("do_login: login out")
            return False
        if d(resourceId="com.icbc:id/tv_exit_login").exists(timeout=5):
            print("do_login: login")
            return True
        else:
            print("do_login: login out")
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
    if task_name == "is_login":
        is_login()
    if task_name == "go_home":
        d.press("home")
    if task_name == "back":
        d.press("back")
