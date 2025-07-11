import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
#下面两个处理图片的模块
from PIL import Image  #图像处理、加载、转换、保存
from io import BytesIO  #内存中模拟文件对象，处理二进制数据
import hmac
from urllib.parse import urlencode
import os
import json


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise Exception("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    return {'host': host, 'path': path, 'schema': schema}

#  生成带身份鉴权信息的请求URL
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u['host']
    path = u['path']
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    #使用 HMAC-SHA256 算法对签名原文进行加密，密钥是你的 api_secret
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    #对整个授权字符串再次进行 Base64 编码，形成最终的 authorization 参数。
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = 'api_key="{}", algorithm="{}", headers="{}", signature="{}"'.format(
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }
    return requset_url + "?" + urlencode(values)

def image_demo():
    # 配置信息
    APPID = "e5721ff5"
    APIKEY = "701d701231912c6bd8376740ffcabf65"
    APISECRET = "MTYzZjkzYWE4M2RhZjhhNmZmNTIwOGNh"
    url = "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"

    # 构造请求体
    payload = {
        "header": {
            "app_id": APPID,
            "uid": "123456789"
        },
        "parameter": {
            "chat": {
                "domain": "general",
                "temperature": 0.5,
                "max_tokens": 4096,
                "width": 512,
                "height": 512
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "user",
                        "content": "帮我画一座山"
                    }
                ]
            }
        }
    }

    # 生成带鉴权的 URL
    auth_url = assemble_ws_auth_url(url, method="POST", api_key=APIKEY, api_secret=APISECRET)

    # 发起请求
    headers = {"Content-Type": "application/json"}
    response = requests.post(auth_url, json=payload, headers=headers)

    print(response.status_code)
    # print(response.json()["header"]["message"],  response.json()["payload"]["choices"]["text"][0]["content"])

    #生成给图片命名的文件名
    now = datetime.now()
    filename = "image"+now.strftime("%Y-%m-%d %H%M%S") + ".png"
    save_dir= "image"
    save_path = os.path.join(save_dir,filename)
    base64_to_image(response.json()["payload"]["choices"]["text"][0]["content"], save_path)


def base64_to_image(base64_str,save_path):
    #使用方法的demo
    # bio = BytesIO(base64.b64decode(base64_str))  # 把 base64 解码成二进制
    # image = Image.open(bio)  # 用 PIL 打开这个“假文件”
    # image.save("decoded_image.jpg")  # 保存图像
    #这里的解码base64字符串为二进制数据
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    image.save(save_path)
    print(f"图片已经保存在：{save_path}中。")


if __name__ == '__main__':

    image_demo()
