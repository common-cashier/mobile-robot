# coding: utf-8
import json
import base64
import re

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from settings import log

cred = credential.Credential("AKIDRgfLktkKeiW2HFwMVO1NSGo43lCNHuGL", "pNefQu73i5B1cwzlIYWDdngofGadOu97")
httpProfile = HttpProfile()
httpProfile.endpoint = "ocr.tencentcloudapi.com"

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = ocr_client.OcrClient(cred, "ap-hongkong", clientProfile)


def ocr_img(img_url, letters_len):
    try:
        req = models.GeneralBasicOCRRequest()

        with open(img_url, "rb") as f:
            # b64encode是编码，b64decode是解码
            base64_data = str(base64.b64encode(f.read()), "utf-8")
            # base64.b64decode(base64data)
            print(base64_data)

        params = {
            "ImageBase64": base64_data
        }
        req.from_json_string(json.dumps(params))

        resp = client.GeneralBasicOCR(req)

        resp = resp.to_json_string()
        log('ocr_from_tencent: ' + resp, '4')
        rsp_json = json.loads(resp)
        rsp = ''
        for letters in rsp_json['TextDetections']:
            rsp += letters['DetectedText']
        rsp = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", rsp)
        rsp = rsp[0: letters_len]
        # rsp_json_str = resp.to_json_string()
        log('ocr_img_to: ' + rsp, '4')
        return rsp

    except TencentCloudSDKException as err:
        print(err)


if __name__ == '__main__':
    ocr_img("./verification.jpg", 10)
