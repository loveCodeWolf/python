import time
import re
import random  # 添加random模块用于生成随机延时
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

def random_sleep(min_seconds=1, max_seconds=5):
    """
    随机延时函数
    
    Args:
        min_seconds: 最小延时秒数
        max_seconds: 最大延时秒数
    """
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def get_article_links(keyword, max_page=10):
    """
    获取搜狗微信搜索结果中的文章链接
    
    Args:
        keyword: 搜索关键词
        max_page: 最大爬取页数
    
    Returns:
        links_data: 包含文章链接信息的DataFrame
    """
    # 设置Chrome选项
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 无头模式，取消注释可不显示浏览器窗口
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 添加忽略SSL错误的选项
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用日志输出
    
    # 初始化WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 存储所有链接的列表
    all_links = []
    
    try:
        # 循环遍历页面
        for page in range(1, max_page + 1):
            print(f"正在爬取第 {page} 页...")
            
            # 构建URL，使用page参数实现翻页
            url = f"https://weixin.sogou.com/weixin?query={keyword}&type=2&page={page}&ie=utf8"
            driver.get(url)
            
            # 使用随机延时等待页面加载
            random_sleep(2, 5)
            
            # 查找所有的img-box元素
            img_boxes = driver.find_elements(By.CSS_SELECTOR, "div.img-box")
            
            if not img_boxes:
                print(f"第 {page} 页没有找到文章，可能已到达最后一页或需要验证码")
                break
            
            # 遍历每个img-box，提取a标签中的链接
            for box in img_boxes:
                try:
                    # 使用find_element方法获取第一个a标签，因为img-box的兄弟元素中通常包含a标签
                    #这里的By.TAG_NAME用于直接获取<a><div><span>等的标签
                    a_tag = box.find_element(By.TAG_NAME, "a")
                    
                    # 直接获取标签的属性值
                    href = a_tag.get_attribute("href")
                    
                    # 提取文章标题
                    # 找到相关的标题元素 (通常在img-box的兄弟元素中)
                    # By.XPATH：适合需要精确控制层级关系或复杂条件的场景。
                    parent_li = box.find_element(By.XPATH, "./..") #这里是通过xpath语法找到当前元素的父元素，然后通过find_element找到第一个匹配的元素
                    title_element = parent_li.find_element(By.CSS_SELECTOR, "h3 a")
                    title = title_element.text
                    
                    # 提取发布时间和公众号名称
                    #By.CSS_SELECTOR 用于定位 div.img-box 和 h3 a 等元素。
                    info_element = parent_li.find_element(By.CSS_SELECTOR, "div.s-p")
                    account = info_element.find_element(By.CSS_SELECTOR, "span.all-time-y2").text
                    
                    # 将信息添加到列表中
                    all_links.append({
                        "title": title,
                        "link": href,
                        "account": account,
                        "page": page,
                    })
                    
                    print(f"已获取: {title}")
                    
                    # 每获取一条链接后添加短暂的随机延时
                    random_sleep(0.5, 2)
                    
                except Exception as e:
                    print(f"提取链接时出错: {e}")
            
            # 每页爬取完成后添加随机延时，防止请求过快被封
            random_sleep(3, 7)
    
    except Exception as e:
        print(f"爬取过程中出错: {e}")
    
    finally:
        # 关闭浏览器
        driver.quit()
    
    # 将结果转换为DataFrame
    links_df = pd.DataFrame(all_links)
    
    # 保存结果到CSV文件
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, f"{keyword}_article_links.csv")
    links_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"共获取到 {len(all_links)} 条文章链接，已保存到 {output_file}")
    
    return links_df

if __name__ == "__main__":
    # 设置搜索关键词
    search_keyword = "虾谷订阅号2024"
    
    # 设置最大爬取页数
    max_pages = 5
    
    # 获取文章链接
    article_links = get_article_links(search_keyword, max_pages)
    
    # 显示前5条结果
    if not article_links.empty:
        print("\n获取的部分文章链接:")
        print(article_links.head())