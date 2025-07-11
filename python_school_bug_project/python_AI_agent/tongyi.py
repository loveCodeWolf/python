import requests
import json
from get_weather import get_weather
from get_dbData import get_dbData
from get_item import get_item_compare

messages = []
print(messages)

def tongyi_chat(content,url,key):
    global messages

    # 将用户的原始提问（不含注入的知识）添加到全局对话历史
    messages.append({"role": "user", "content": content})

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": messages,
        "stream": False,
        "max_tokens": 512,
        "enable_thinking": True,
        "thinking_budget": 4096,
        "min_p": 0.05,
        "stop": [],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "仅当用户明确提供城市和要求了解天气状况时才使用这个工具。获取指定城市的详细天气信息",
                    "name": "get_weather",
                    "parameters": {
                        "city" :{
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "description": "仅当用户明确指定说明对应的数据库的名称和操作时使用这个工具。对指定数据库进行操作，如果是不同的数据库则需要多次调用这个函数，但如果是同一个数据库的操作的话就执行一次就好",
                    "name": "get_dbData",
                    "parameters": {
                        "databaseName": {
                            "type": "string",
                            "description": "数据库名"
                        },
                        "tableName": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "表名（这里将需要操作的表名一一放入这个数组中）"
                        },
                        "measures": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "对于mysql数据库的sql操作代码（按顺序一条条放入进去）"
                        }
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "description": "仅当用户明确提供淘宝或天猫商品链接同时链接中有商品链接，并且要求比较商品链接时调用这个工具。不要在用户没有提供具体链接时调用此函数。",
                    "name": "get_item_compare",
                    "parameters": {
                        "file_path": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "如果用户输入的要求是几个类似于‘https://item.taobao.com/item.htm?id=887862383399’这样的链接地址让你进行比较或者进行介绍一下这几个商品，你就将这几个链接中的id的参数放入这个数组中"
                        },
                        "measures": {
                            "type": "int",
                            "description": "对淘宝商品链接网址的操作，如果是要进行比较的话在这里的参数中输入1、如果是要进行介绍这几个商品的链接的话输入2"
                        }
                    },
                    "strict": True
                }
            },
        ]
    }
    headers = {
        "Authorization": "Bearer "+key,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # 将响应的结果转换为字典
    result = response.json()
    print(result)
    if "choices" not in result or not result["choices"]:
        print("Error: API response does not contain 'choices'.")
        # 即使API出错，也记录用户的原始提问
        messages.append({"role": "user", "content": content})
        error_response = "抱歉，调用模型时发生错误，未能获取回复。"
        messages.append({"role": "assistant", "content": error_response})
        return error_response
    #获取模型返回的消息内容
    message_from_model = result["choices"][0]["message"]
    
    end_chat_push = call_function(message_from_model)
    return end_chat_push


def song_toText(file_path, url, key):
    model = "FunAudioLLM/SenseVoiceSmall"
    headers = {
        "Authorization": f"Bearer {key}"
    }

    with open(file_path, "rb") as audio_file:
        files = {
            "model": (None, model),
            "file": (file_path, audio_file, "audio/mpeg")  #支持mp3文件
        }
        response = requests.post(url, headers=headers, files=files)

    return response.json()


#这里的是处理tools中有输出的情况,来调用外部的tools
def call_function(message):
    # 判断是否有 tool_calls，进行方法的调用
    entire_ResponseText = ''
    if "tool_calls" in message:
        for call in message["tool_calls"]:
            if call["function"]["name"] == "get_weather":
                # 解析参数
                args = json.loads(call["function"]["arguments"])
                city = args["city"]
                # 调用本地函数
                tool, weather_info = get_weather(city)
                ai_response = weather_info
                messages.append({"role": "assistant", "content": ai_response})
                entire_ResponseText += f"调用 get_weather({city}) 得到结果：使用了：{tool}大模型，输出的天气的结果是：{ai_response}"
            elif call["function"]["name"] == "get_dbData":
                args = json.loads(call["function"]["arguments"])
                databaseName = args["databaseName"]
                tableName = args["tableName"]
                measures = args["measures"]
                # 调用本地函数
                tool, db_data = get_dbData(databaseName, tableName, measures)
                ai_response = db_data
                messages.append({"role": "assistant", "content": ai_response})
                entire_ResponseText += f"调用 get_dbData({databaseName}, {tableName}, {measures}) 获得结果：使用了：{tool}大模型，输出的数据库的操作结果是：{ai_response}"
            elif call["function"]["name"] == "get_item_compare":
                args = json.loads(call["function"]["arguments"])
                file_path = args["file_path"]
                measures = args["measures"]
                # 调用本地函数
                tool, thinking, product_reason = get_item_compare(file_path, measures)
                ai_response = product_reason
                messages.append({"role": "assistant", "content": ai_response})
                entire_ResponseText += f"调用 get_item_compare({file_path}, {measures}) 获得结果：使用了：{tool}大模型，输出的推荐的商品和原因：{ai_response}"
        return "总的返回效果："+entire_ResponseText
    else:
        ai_response = message["content"]
        # 将 AI 的回复也加入上下文，供下次使用
        messages.append({"role": "assistant", "content": ai_response})
        return "没有调用任何工具，模型直接给出了回答：\n"+ ai_response

if __name__ == '__main__':
    url_chats = "https://api.siliconflow.cn/v1/chat/completions"
    # url_image = "https://api.siliconflow.cn/v1/images/generations"
    # url_song = "https://api.siliconflow.cn/v1/audio/transcriptions"

    key = "sk-wrilwzaclgftxgshxeienqtsjjmuqegomwhqeiskkmevvcpb"


    #这里的是对话的API

    # function  = "在这里你是一个专业的对话高手，你的主要任务是精确的回答user的每一个问题，回答的好会给你丰厚的奖励！"
    # content = content + input("请输入你的问题：")
    # result = tongyi_chat(content,url_chats,key,function)
    # print(result["model"], result["choices"][0]["message"]["content"])

    #这里的是有调用函数的大模型

    function = """你是一个智能助手，能够理解用户的自然语言请求，并直接给出回答，只有用户的要求达到了调动工具的标准才可以调用。
        重要约束：
        2. 绝对不要使用工具描述中的示例链接或ID
        3. 绝对不要"脑补"或"想象"用户没有提供的链接
        4. 如果用户只是询问功能或进行一般对话，请直接回答，不要调用任何工具
        5. 只能基于用户在当前消息中实际提供的内容进行工具调用）"""
    messages.append({"role": "system", "content": function})
    while True:
        content = ""
        content = content+input("请输入你的问题：")
        print(messages)
        result = tongyi_chat(content, url_chats, key)
        print(result)

    # 这里的是专业的翻译助手
    # function  = "在这里你是一个专业的翻译助手，你的主要任务是精确的翻译user的每一个问题，将他发给你的句子翻译成英文，翻译的好会给你丰厚的奖励！"
    # content = content + input("请输入你要翻译的中文：")
    # result = tongyi_chat(content,url_chats,key,function)
    # print(result["model"], result["choices"][0]["message"]["content"])

    #这里的是音频的方式转为文字
    # file_path = "LightYear光年 - 简简单单.mp3"  # 替换为你自己的文件路径
    # print(song_toText(file_path, url_song, key)["text"])



