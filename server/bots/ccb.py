import sys

sys.path.append("..")
import settings
from bots.verification.verification_code_boc import VerificationCodeBoc

package = 'com.chinamworld.bocmbci'
activity = 'com.boc.bocsoft.mobile.bocmobile.buss.system.main.ui.MainActivity'
self = settings.bot.device


def start():
    self.screen_on()
    settings.bot.pid = self.app_start(package)
    return self.app_wait(package)  # 等待应用运行, return pid(int)


def stop():
    self.app_stop(package)


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
        x = start_info['bounds']['left']
        y = 1448
        width = int(start_info['bounds']['left']) + int(start_info['bounds']['right'])
        height = 135
        img = "verification.jpg"
        self.sleep(2)
        self.screenshot(img)
        vc = VerificationCodeBoc(x, y, width, height, img)
        pwd_code = vc.image_str()
        for letter in pwd_code:
            if letter.isdigit() and int(letter) in arr:
                arr.remove(int(letter))
        print("--------------------------------")
        print(arr)
        print(pwd_code)
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
            print("i = %s and j= %s and original[str(j)] = %s" % (i, j, original[str(j)]))
            j += 1
        print(switcher)
        for l in settings.bot.account.login_pwd:
            print(">>>>>>>>>>-------->")
            print(l)
            print(l.isupper())
            if l.isupper():
                print(l.lower())
                btn_xy = switcher.get(l.lower())
                ca_xy = switcher.get("ca")
                self.sleep(1)
                self.click(ca_xy[0], ca_xy[1])
                self.sleep(1)
                self.click(btn_xy[0], btn_xy[1])
                self.sleep(1)
                self.click(ca_xy[0], ca_xy[1])
                print(btn_xy)
                print(l)
            else:
                btn_xy = switcher.get(l)
                self.sleep(1)
                self.click(btn_xy[0], btn_xy[1])
                print(btn_xy)
                print(l)
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


def do_work(task_name):
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
