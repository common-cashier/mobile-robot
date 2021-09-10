# coding: utf-8
import re  # 用于正则
from PIL import Image  # 用于打开图片和对图片处理
import pytesseract  # 用于图片转文字
import time
Image.LOAD_TRUNCATED_IMAGES = True
import sys
sys.path.append('../..')
from ocr_api import ocr_img


class VerificationCode:
    def __init__(self, x=None, y=None, width=None, height=None, img=None, bank=None, letters_len=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img
        self.bank = bank
        self.letters_len = letters_len

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
        return images

    def image_str(self, deluxe=False):
        # pytesseract.pytesseract.tesseract_cmd = r"/data/data/com.termux/files/usr/bin/tesseract"  # 设置pyteseract路径

        image = self.delete_spot()
        image.save(self.img)

        # pytesseract.image_to_string(image, lang='eng',
        # config="--psm 6 --tessdata-dir bots/verification/tessdata")  # 图片转文字
        # cv_code = OpencvCode(self.img)
        # result_four = cv_code.read_code()
        # pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"  # 设置pyteseract路径
        if deluxe:
            try:
                res = ocr_img(self.img, self.letters_len)
            except Exception as ext:
                res = ''
                print(ext)
        else:
            result = pytesseract.image_to_string(image, lang='eng', config="--psm 6 --tessdata-dir "
                                                                           "bots/verification/tessdata "
                                                                           "--oem 3 -c tessedit_char_whitelist=0123456789")  # 图片转文字
            results = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", result)  # 去除识别出来的特殊字符
            res = results[0:self.letters_len]  # 只获取前self.letters_len个字符
        return res


if __name__ == '__main__':
    a = VerificationCode(0, 0, 1080, 430, 'verification.jpg', "boc", 10)
    code = a.image_str()
    print("img_read: " + code)
