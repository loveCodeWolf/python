# encoding:UTF-8
import json
import requests


# 请替换XXXXXXXXXX为您的 APIpassword, 获取地址：https://console.xfyun.cn/services/bmx1
api_key = "Bearer XXXXXXXXXXXXXXXXXXXX"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 请求模型，并将结果输出
def get_answer(message):
    #初始化请求体
    headers = {
        'Authorization':api_key,
        'content-type': "application/json"
    }
    body = {
        "model": "4.0Ultra",
        "user": "user_id",
        "messages": message,
        # 下面是可选参数
        "stream": True,
        "tools": [
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode":"deep"
                }
            }
        ]
    }
    full_response = ""  # 存储返回结果
    isFirstContent = True  # 首帧标识

    response = requests.post(url=url,json= body,headers= headers,stream= True)
    # print(response)
    for chunks in response.iter_lines():
        # 打印返回的每帧内容
        # print(chunks)
        if (chunks and '[DONE]' not in str(chunks)):
            data_org = chunks[6:]

            chunk = json.loads(data_org)
            text = chunk['choices'][0]['delta']

            # 判断最终结果状态并输出
            if ('content' in text and '' != text['content']):
                content = text["content"]
                if (True == isFirstContent):
                    isFirstContent = False
                print(content, end="")
                full_response += content
    return full_response


# 管理对话历史，按序编为列表
def getText(text,role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

# 获取对话中的所有角色的content长度
def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

# 判断长度是否超长，当前限制8K tokens
def checklen(text):
    while (getlength(text) > 11000):
        del text[0]
    return text


#主程序入口
if __name__ =='__main__':

    #对话历史存储列表
    chatHistory = []
    #循环对话轮次
    while (1):
        # 等待控制台输入
        Input = input("\n" + "我:")
        question = checklen(getText(chatHistory,"user", Input))
        # 开始输出模型内容
        print("星火:", end="")
        getText(chatHistory,"assistant", get_answer(question))