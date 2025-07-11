#这里的文件的操作是进行对于输入的链接进行对商品的详细的信息的获取和对于商品的评价的语句进行获取，最后通过ai进行总结分析
import requests
from get_taobao_context import main
from get_taobao_index import get_taobao_index_2
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

#获取输入的链接，进行获取网页中的商品的id，从而获取商品的评论信息
def compare(content, function):

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
    print(response.text)
    result = response.json()

    try:
        arguments_str = result['choices'][0]['message']['tool_calls'][0]['function']['arguments']
        arguments_dict = json.loads(arguments_str)  # 将字符串转换为字典
        product_id = arguments_dict.get('product_id')
        reason = arguments_dict.get('reason')
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print("解析或访问字段失败:", e)
        product_id = None
        reason = None
    product = f"\n你应该选择这个商品：https://detail.tmall.com/item.htm?id={product_id},原因是：{reason}"
    return result["model"], result["choices"][0]["message"]["reasoning_content"],product
def get_item_compare(item_ids,measures):
    all_feedback = []
    if  measures == 1:
        def fetch_item_data(item_id):
            try:
                feedback = main(item_id)
                result = get_taobao_index_2(item_id)
                item_detail = result["formatted_description"] if result else ""
            except Exception as e:
                print(f"获取商品信息失败: {e}")
                feedback = ""
                item_detail = ""
            return {"item_id": item_id, "feedback": feedback, "item_detail": item_detail}

        # 使用线程池并发获取商品信息
        with ThreadPoolExecutor(max_workers=5) as executor:  # 可根据实际情况调整并发数
            future_to_item = {executor.submit(fetch_item_data, item_id): item_id for item_id in item_ids}
            for future in as_completed(future_to_item):
                data = future.result()
                all_feedback.append(data)

        # 将所有反馈内容合并为一个字符串传给 AI 分析
        combined_feedback = "\n\n".join([f"商品id: {fb['item_id']} 的评价:\n{fb['feedback']}商品详细信息:\n{fb['item_detail']}" for fb in all_feedback])

        function = "你是一个商品的评价的能手，我会给你每个商品的评价的内容，你要按我给你的这些评论或者商品的详细信息给我做一下比较和评价，最后推荐用户购买哪一个商品的商品id号,同时给出选择这个商品的原因"
        return compare(combined_feedback, function)
    elif measures == 2:
        return "产品正在开发中尽情期待"
    else:
        return "无效的操作类型"

