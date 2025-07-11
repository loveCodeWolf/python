# import json
# import hashlib
# import random
# import time
#
# import pandas as pd
# import requests
#
# results = []
#
#
# def fetch_review_list(datas, md5_hash,t):
#     url = "https://h5api.m.tmall.com/h5/mtop.alibaba.review.list.for.new.pc.detail/1.0/"
#     params = {
#         "jsv": "2.7.2",
#         "appKey": "12574478",
#         "t": t,  # 使用当前时间戳
#         "sign": md5_hash,  # 请替换为实际的签名值
#         "api": "mtop.alibaba.review.list.for.new.pc.detail",
#         "v": "1.0",
#         "isSec": "0",
#         "ecode": "0",
#         "timeout": "20000",
#         "ttid": "2022@taobao_litepc_9.17.0",
#         "AntiFlood": "true",
#         "AntiCreep": "true",
#         "preventFallback": "true",
#         "type": "jsonp",
#         "dataType": "jsonp",
#         "callback": "mtopjsonp6",
#         "data": datas
#     }
#     # 设置 headers
#     headers = {
#         "Cookie": "自己的"
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
#         "Referer": "https://detail.tmall.com/",
#         "Accept": "*/*",
#         "Connection": "keep-alive"
#     }
#
#     response = requests.get(url, params=params, headers=headers)
#     print(response.text)
#     json_content = json.loads(response.text.replace("mtopjsonp6(", "").replace("})", "}"))
#     # 获取评论区
#     counten = json_content['data']['module']['reviewVOList']
#     rulist =[]
#     for i in counten:
#         pinglun = i['reviewWordContent']
#         rulist.append(pinglun)
#     return  rulist
#
# def taobao(sign, datas, appkey, t,coci):
#     # 构造 URL 和参数
#     url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
#     params = {
#         "jsv": "2.7.0",
#         "appKey": appkey,
#         "t": t,
#         "sign": sign,
#         "api": "mtop.relationrecommend.WirelessRecommend.recommend",
#         "v": "2.0",
#         "H5Request": "true",
#         "preventFallback": "true",
#         "type": "jsonp",
#         "dataType": "jsonp",
#         "callback": "mtopjsonp2",
#         "data": datas
#     }
#
#     # 设置 headers
#     headers = {
#         "Cookie": coci,
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Referer": "https://h5.m.taobao.com/",
#         "Accept": "*/*",
#         "Connection": "keep-alive"
#     }
#
#     # 发起请求
#     response = requests.get(url, headers=headers, params=params)
#     # 确保请求成功
#     if response.status_code == 200:
#         content = response.text.replace("mtopjsonp2(", "").replace("})", "}")
#
#         # 检查响应内容是否为空
#         if content.strip():
#             # 解析JSON字符串
#             try:
#                 json_content = json.loads(content)
#                 # 获取指定的JSON内容
#                 name = json_content['data']['itemsArray']
#
#                 for list in range(len(name)):
#
#                     # 商品链接
#                     product_url = name[list]['auctionURL']
#                     pic_path = name[list]['pic_path']
#                     title = name[list]['title']
#                     print(title)
#                     price = name[list]['priceShow']['price']
#                     # 标签
#                     tag = name[list]['structuredShopInfo']['infoList'][0]['text']
#                     # 销量
#                     sales = name[list]['realSales']
#                     time.sleep(random.randint(1, 5))
#
#                     # 获取评论区
#                     # 商品id
#                     pl_id = name[list]['item_id']
#                     pl_token = "自己的token"
#                     pl_t = str(1718204461753)
#                     pl_appKey = "12574478"
#                     pl_data = '{"itemId":"' + str(pl_id) + '","bizCode":"ali.china.tmall","channel":"pc_detail","pageSize":20,"pageNum":1}'
#                     md5_hash = md5_encrypt(pl_token + "&" + pl_t + "&" + pl_appKey + "&" + pl_data)
#                     print("获取评论区")
#                     pinglunqu = fetch_review_list(pl_data, md5_hash,pl_t)
#
#                     results.append([pl_id,product_url, pic_path, title, price, tag, sales,pinglunqu])
#                     time.sleep( random.randint(1, 5))
#
#             except json.JSONDecodeError as e:
#                 print(f"JSON解析错误: {e}")
#             except KeyError as e:
#                 print(f"键错误: {e}")
#             except IndexError as e:
#                 print(f"索引错误: {e}")
#         else:
#             print("响应内容为空")
#     else:
#         print(f"请求失败，状态码: {response.status_code}")
#
#
# def md5_encrypt(data):
#     """对给定的数据进行MD5加密"""
#     md5_obj = hashlib.md5()
#     md5_obj.update(data.encode('utf-8'))  # 确保数据是字节类型
#     return md5_obj.hexdigest()  # 返回16进制格式的哈希值
#
#
# if __name__ == '__main__':
#
#     keyword = "碎花裙"
#     token = "5bd761b5be355"
#     t = str(int(time.time() * 1000))
#     appKey = "12574478"
#     coci="自己的Cookie"
#     for page in range(30, 50):
#         data = '{"appId":"29859","params":"{\\"isBeta\\":\\"false\\",\\"grayHair\\":\\"false\\",\\"appId\\":\\"29859\\",\\"from\\":\\"\\",\\"brand\\":\\"HUAWEI\\",\\"info\\":\\"wifi\\",\\"index\\":\\"4\\",\\"ttid\\":\\"600000@taobao_android_10.7.0\\",\\"needTabs\\":\\"true\\",\\"rainbow\\":\\"\\",\\"areaCode\\":\\"CN\\",\\"vm\\":\\"nw\\",\\"schemaType\\":\\"auction\\",\\"elderHome\\":\\"false\\",\\"device\\":\\"HMA-AL00\\",\\"isEnterSrpSearch\\":\\"true\\",\\"newSearch\\":\\"false\\",\\"network\\":\\"wifi\\",\\"subtype\\":\\"\\",\\"hasPreposeFilter\\":\\"false\\",\\"client_os\\":\\"Android\\",\\"gpsEnabled\\":\\"false\\",\\"searchDoorFrom\\":\\"srp\\",\\"debug_rerankNewOpenCard\\":\\"false\\",\\"homePageVersion\\":\\"v7\\",\\"searchElderHomeOpen\\":\\"false\\",\\"style\\":\\"wf\\",\\"page\\":' + str(
#             page) + ',\\"n\\":\\"10\\",\\"q\\":\\"' + keyword + '\\",\\"search_action\\":\\"initiative\\",\\"sugg\\":\\"_4_1\\",\\"m\\":\\"h5\\",\\"sversion\\":\\"13.6\\",\\"prepositionVersion\\":\\"v2\\",\\"tab\\":\\"all\\",\\"channelSrp\\":\\"\\",\\"tagSearchKeyword\\":null,\\"sort\\":\\"_sale\\",\\"filterTag\\":\\"\\",\\"prop\\":\\"\\",\\"item_id\\":\\"\\\"}"}'
#         md5_hash = md5_encrypt(token + "&" + t + "&" + appKey + "&" + data)
#         print(page)
#         taobao(md5_hash, data, appKey, t,coci)
#
#     df = pd.DataFrame(results, columns=['商品id','商品链接', '图片路径', '标题', '价格', '标签', '销量','用户评论'])
#     df.to_excel('淘宝1.xlsx', index=False, engine='openpyxl')
#
#     # 根据销量高的产品来获取他们的评论
#
