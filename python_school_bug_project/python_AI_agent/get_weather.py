# import json


#城市搜索
#curl -X GET --compressed \
#-H 'Authorization: Bearer your_token' \
#'https://your_api_host/geo/v2/city/lookup?location=beij'

#查询目前的天气情况：
# curl -X GET --compressed \
# -H 'Authorization: Bearer your_token' \
# 'https://your_api_host/v7/weather/now?location=101010100'

import requests

def get_city_number(city):
    url = f"https://n35vxk8hb8.re.qweatherapi.com/geo/v2/city/lookup?location={city}"  # 这里的接口是获取当天的现在的时间点的天气状况
    headers = {
        "X-QW-Api-Key": "92648c1ee5eb496782a4048b97aa792d"
    }
    request = requests.get(url, headers=headers)
    data = request.json()
    if data["code"] == "200":
        city_number = data["location"][0]["id"]
        print(city_number)
        return city_number
    else:
        return None

def format_weather_data(data):
    """
        格式化天气数据并返回字符串
        :param data: 天气API返回的数据字典
        :return: 格式化后的天气信息字符串
        """
    now = data.get("now", {})
    return (
        f"更新时间：{data.get('updateTime', 'N/A')}\n"
        f"观测时间：{now.get('obsTime', 'N/A')}\n"
        f"温度：{now.get('temp', 'N/A')}°C\n"
        f"体感温度：{now.get('feelsLike', 'N/A')}°C\n"
        f"天气状况：{now.get('text', 'N/A')}\n"
        f"风向：{now.get('windDir', 'N/A')} ({now.get('wind360', 'N/A')}°)\n"
        f"风力等级：{now.get('windScale', 'N/A')}级\n"
        f"风速：{now.get('windSpeed', 'N/A')}公里/小时\n"
        f"相对湿度：{now.get('humidity', 'N/A')}%\n"
        f"降水量（过去1小时）：{now.get('precip', 'N/A')}毫米\n"
        f"大气压强：{now.get('pressure', 'N/A')}百帕\n"
        f"能见度：{now.get('vis', 'N/A')}公里\n"
        f"云量：{now.get('cloud', 'N/A')}%\n"
        f"露点温度：{now.get('dew', 'N/A')}°C\n"
        f"\n更多信息请访问：{data.get('fxLink', 'N/A')}"
    )
def get_today_weather(city):
    url = f"https://n35vxk8hb8.re.qweatherapi.com/v7/weather/now?location={city}"  # 这里的接口是获取当天的现在的时间点的天气状况
    print(url)
    headers={
        "X-QW-Api-Key": "92648c1ee5eb496782a4048b97aa792d"
    }
    request = requests.get(url,  headers=headers)
    function = "你是一个温柔的天气助手，你的工作就是将输入的详细天气的内容做一个总结输出一段天气的介绍，要求是既要有天气的状况也要有以这些天气状况提醒注意带伞，防晒等的个性化关怀。"
    data = weather_chat(format_weather_data(request.json()), function)

    return data

def weather_chat(content, function):

    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "system",
                "content": function
            },
            {
                "role": "user",
                "content": content
            }],
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
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }
    headers = {
        "Authorization": "Bearer sk-wrilwzaclgftxgshxeienqtsjjmuqegomwhqeiskkmevvcpb",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    result =  response.json()
    # return result["model"], result["choices"][0]["message"]["content"],result["choices"][0]["message"]["reasoning_content"]
    return result["model"], result["choices"][0]["message"]["content"]
def get_weather(city):
    return get_today_weather(get_city_number(city))

# if __name__ == "__main__":
#     # 示例调用
#     # weather_data = get_today_weather(get_city_number("北京"))  # 获取天气数据
#     # formatted_output = format_weather_data({'code': '200', 'updateTime': '2025-05-23T15:42+08:00', 'fxLink': 'https://www.qweather.com/weather/beijing-101010100.html', 'now': {'obsTime': '2025-05-23T15:40+08:00', 'temp': '22', 'feelsLike': '21', 'icon': '104', 'text': '阴', 'wind360': '0', 'windDir': '北风', 'windScale': '1', 'windSpeed': '5', 'humidity': '34', 'precip': '0.0', 'pressure': '1011', 'vis': '24', 'cloud': '91', 'dew': '9'}, 'refer': {'sources': ['QWeather'], 'license': ['QWeather Developers License']}})  # 格式化输出
#     # print(formatted_output)
#
#     print(get_weather("绍兴"))


