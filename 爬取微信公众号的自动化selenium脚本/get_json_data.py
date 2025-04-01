import requests
import json
import csv
import time
import random
import os
import re

def random_sleep(min_seconds=1, max_seconds=3):
    """随机延时函数"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def fetch_wechat_articles():
    """
    从微信公众号接口获取文章列表，提取标题中包含"虾谷龙虾报价"的文章链接
    """
    # 基础URL
    base_url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    
    # 请求参数
    params = {
        "action": "list_ex",
        "fakeid": "MzkyMTY0Nzg4Mg==",
        "query": "",
        "begin": 0,
        "count": 4,
        "type": 9,
        "need_author_name": 1,
        "fingerprint": "82fa863c4e64d691848c89967c25cb6b",
        "token": "1630039504",
        "lang": "zh_CN",
        "f": "json",
        "ajax": 1
    }
    
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": "",  # 需要替换为你的实际Cookie
        "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&lang=zh_CN&token=1630039504"
    }
    
    # 存储所有符合条件的文章
    all_articles = []
    
    # 当前页码
    page = 1
    
    # 总文章数
    total_count = 0
    
    # 正则表达式，匹配"几年几月几日虾谷龙虾报价"格式的标题
    title_pattern = re.compile(r'\d+年\d+月\d+日虾谷龙虾报价')
    
    try:
        # 循环获取所有页面的文章
        while True:
            print(f"正在获取第 {page} 页文章...")
            
            # 发送请求
            response = requests.get(base_url, params=params, headers=headers)
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                break
            
            # 解析响应数据
            data = response.json()
            
            # 检查是否成功
            """
            - 检查从微信公众平台API返回的JSON数据中的 base_resp 字段下的 ret 值
            - 在微信API中， ret 值为0表示请求成功，非0值表示请求失败"""

            if data["base_resp"]["ret"] != 0:
                print(f"获取数据失败: {data['base_resp']['err_msg']}")
                break
            
            # 获取总文章数
            if page == 1:
                total_count = data["app_msg_cnt"]
                print(f"公众号共有 {total_count} 篇文章")
            
            # 提取文章列表
            articles = data["app_msg_list"]
            
            # 如果没有更多文章，退出循环
            if not articles:
                print("没有更多文章")
                break
            
            # 遍历文章列表
            for article in articles:
                title = article["title"]
                
                # 检查标题是否符合条件
                if title_pattern.search(title):  ##正则匹配校验
                    link = article["link"]
                    create_time = article["create_time"]
                    
                    # 将信息添加到列表中
                    all_articles.append({
                        "title": title,
                        "link": link,
                        "create_time": create_time
                    })
                    
                    print(f"已获取: {title}")
            
            # 更新begin参数，获取下一页
            params["begin"] += 4
            page += 1
            
            # 随机延时，避免被封
            random_sleep(2, 5)
            
            # 如果已经获取了所有文章，退出循环
            if params["begin"] >= 12:
                print("已获取所有文章")
                break
    
    except Exception as e:
        print(f"获取文章时出错: {e}")
    
    # 按创建时间排序
    """
    - lambda x: x["create_time"] 是一个匿名函数
    - 对于列表中的每个元素 x （即每篇文章的字典），取其 create_time 字段的值作为排序依据"""
    all_articles.sort(key=lambda x: x["create_time"], reverse=True)
    
    # 将结果保存为CSV文件
    """
    - os.path.abspath() 函数将路径转换为绝对路径，解决可能存在的相对路径问题。这确保了无论从哪里调用这个脚本，都能获得正确的完整路径。
    - os.path.dirname() 函数从文件的完整路径中提取出目录部分，去掉文件名。"""
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "虾谷龙虾报价_articles.csv")  ##保存为csv文件
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)  # 创建一个CSV写入器
        # 写入表头
        writer.writerow(["title", "link"])
        # 写入数据
        for article in all_articles:
            """
            writer.writerow() 方法需要接收一个可迭代对象（通常是列表或元组）作为参数，表示要写入CSV文件的一行数据"""
            writer.writerow([article["title"], article["link"]])
    
    print(f"共获取到 {len(all_articles)} 篇文章，已保存到 {output_file}")
    
    return all_articles

if __name__ == "__main__":
    fetch_wechat_articles()