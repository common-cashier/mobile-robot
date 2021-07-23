# coding: utf-8
import re  # 用于正则

from PIL import Image  # 用于打开图片和对图片处理
import pytesseract  # 用于图片转文字
import time
Image.LOAD_TRUNCATED_IMAGES = True

class VerificationCodeBoc:
    def __init__(self, x=None, y=None, width=None, height=None, img=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img

    def get_pictures(self):
        page_snap_obj = Image.open(self.img)
        # page_snap_obj = Image.open('pictures.jpg')
        time.sleep(1)
        # location = img.location
        # size = img.size  # 获取验证码的大小参数
        # left = 0
        # top = 2216
        # right = left + 1435
        # bottom = top + 757
        left = self.x
        top = self.y
        right = left + self.width
        bottom = top + self.height
        image_obj = page_snap_obj.crop((left, top, right, bottom))  # 按照验证码的长宽，切割验证码
        # image_obj.show()  # 打开切割后的完整验证码
        # self.driver.close()  # 处理完验证码后关闭浏览器
        return image_obj

    def processing_image(self):
        image_obj = self.get_pictures()  # 获取验证码
        img = image_obj.convert("L")  # 转灰度
        # ret, img = cv2.threshold(np.array(img), 125, 255, cv2.THRESH_BINARY)
        Bigdata = img.load()
        w, h = img.size
        threshold = 120
        # 遍历所有像素，大于阈值的为黑色
        for y in range(h):
            for x in range(w):
                if Bigdata[x, y] < threshold:
                    Bigdata[x, y] = 0
                else:
                    Bigdata[x, y] = 255
        # img.show()
        return img

    def delete_spot(self):
        images = self.processing_image()
        data = images.getdata()
        w, h = images.size
        black_point = 0
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                mid_pixel = data[w * y + x]  # 中央像素点像素值
                if mid_pixel < 50:  # 找出上下左右四个方向像素点像素值
                    top_pixel = data[w * (y - 1) + x]
                    left_pixel = data[w * y + (x - 1)]
                    down_pixel = data[w * (y + 1) + x]
                    right_pixel = data[w * y + (x + 1)]
                    # 判断上下左右的黑色像素点总个数
                    if top_pixel < 10:
                        black_point += 1
                    if left_pixel < 10:
                        black_point += 1
                    if down_pixel < 10:
                        black_point += 1
                    if right_pixel < 10:
                        black_point += 1
                    if black_point < 1:
                        images.putpixel((x, y), 255)
                    black_point = 0
        images.save(self.img)
        return images

    def image_str(self):
        # pytesseract.pytesseract.tesseract_cmd = r"/data/data/com.termux/files/usr/bin/tesseract"  # 设置pyteseract路径

        image = self.delete_spot()
        image.save(self.img)
        # pytesseract.image_to_string(image, lang='eng',
        # config="--psm 6 --tessdata-dir bots/verification/tessdata")  # 图片转文字
        # cv_code = OpencvCode(self.img)
        # result_four = cv_code.read_code()
        # pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"  # 设置pyteseract路径
        result = pytesseract.image_to_string(image, lang='eng', config="--psm 6 --tessdata-dir "
                                                                       "bots/verification/tessdata "
                                                                       "--oem 3 -c tessedit_char_whitelist=0123456789")  # 图片转文字
        print(result)
        results = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", result)  # 去除识别出来的特殊字符
        res = results[0:10]  # 只获取前10个字符
        print(res)  # 打印识别的验证码
        return res


if __name__ == '__main__':
    a = VerificationCodeBoc(0, 0, 720, 430, 'verification.jpg')
    code = a.image_str()
    passwd = list("080706")
    switcher2 = {
        0: [0.498, 0.964],
        1: [0.166, 0.752],
        2: [0.504, 0.751],
        3: [0.834, 0.751],
        4: [0.17, 0.82],
        5: [0.502, 0.825],
        6: [0.832, 0.825],
        7: [0.166, 0.897],
        8: [0.5, 0.892],
        9: [0.822, 0.889],
    }
    for i in passwd:
        print("----------------------------->>>")
        print("i", i)
        for j in code:
            print("j", j)
            if i == j:
                print("match", j)
                if code.index(j) + 1 != 10:
                    key_inx = code.index(j) + 1
                else:
                    key_inx = 0
                print("index", key_inx)
                btn_xy = switcher2.get(int(key_inx), "Invalid key")
                print(btn_xy)
