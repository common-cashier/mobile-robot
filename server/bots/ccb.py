import datetime
import os
import sys

sys.path.append("..")
import api
import settings
from bots.verification.verification_code import VerificationCode

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
    else:
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


def go_to_transaction():
    return


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
        settings.need_receipt = True
        settings.last_transferee = settings.transferee
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
    if task_name == "go_home":
        self.press("home")
    if task_name == "back":
        self.press("back")
