import pandas as pd
import json
import time
import random
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def random_sleep(min_seconds=1, max_seconds=3):
    """随机延时函数"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def extract_date_from_title(title):
    """从文章标题中提取日期"""
    date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
    match = re.search(date_pattern, title)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None

def extract_price_data():
    """
    从CSV文件中读取链接，访问每个链接并提取小龙虾价格数据
    """
    # 设置当前工作目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 读取CSV文件
    # csv_file = os.path.join(current_dir, "虾谷订阅号_article_links.csv")
    csv_file = os.path.join(current_dir, "虾谷龙虾报价_articles.csv")
    if not os.path.exists(csv_file):
        print(f"错误：找不到文件 {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    
    # 检查是否有link列
    if 'link' not in df.columns:
        print("错误：CSV文件中没有'link'列")
        return
    
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
    """ChromeDriverManager().install() 会自动下载与当前Chrome浏览器版本兼容的ChromeDriver
        Service() 创建一个服务对象，用于管理ChromeDriver进程"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 存储所有价格数据的列表
    all_price_data = []
    
    try:
        # 遍历每个链接
        for index, row in df.iterrows():
            link = row['link']
            title = row['title']
            
            # 从标题中提取日期
            date = extract_date_from_title(title)
            if not date:
                print(f"无法从标题中提取日期: {title}")
                continue
                
            print(f"正在处理第 {index+1}/{len(df)} 篇文章: {title} (日期: {date})")
            
            try:
                # 访问链接
                driver.get(link)
                
                # 等待页面加载
                random_sleep(2, 4)
                
                # 等待文章内容元素出现
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "js_content"))
                    )
                except Exception as e:
                    print(f"等待文章内容超时: {e}")
                    continue
                
                # 获取文章内容
                content_element = driver.find_element(By.ID, "js_content")
                
                # 使用BeautifulSoup解析内容
                html_content = content_element.get_attribute('innerHTML')
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 提取表格数据
                tables = soup.find_all('table')
                if not tables:
                    print(f"文章中没有找到表格: {title}")
                    continue
                
                # 假设第一个表格是小龙虾价格表
                price_table = tables[0]
                
                # 提取表格行
                rows = price_table.find_all('tr')
                if len(rows) < 2:  # 至少需要表头和一行数据
                    print(f"表格格式不正确: {title}")
                    continue
                
                # 提取表头
                headers = []
                header_cells = rows[1].find_all(['td', 'th'])  # 第二行通常是真正的表头
                for cell in header_cells:
                    header_text = cell.get_text(strip=True).replace('\n', '').replace('\r', '')
                    headers.append(header_text)
                
                # 检查表头是否包含所需的列
                expected_headers = ['品种', '规格', '价格', '对比昨天']
                if not all(any(expected in header for header in headers) for expected in expected_headers):
                    print(f"表格不包含所需的列: {title}")
                    continue
                
                # 提取数据行
                price_data = []
                for row in rows[2:]:  # 从第三行开始是数据
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # 确保有足够的单元格
                        variety = cells[0].get_text(strip=True).replace('\n', '').replace('\r', '')
                        spec = cells[1].get_text(strip=True).replace('\n', '').replace('\r', '')
                        price = cells[2].get_text(strip=True).replace('\n', '').replace('\r', '')
                        compare = cells[3].get_text(strip=True).replace('\n', '').replace('\r', '')
                        
                        price_data.append({
                            '品种': variety,
                            '规格': spec,
                            '价格': price,
                            '对比昨天': compare
                        })
                
                # 将数据添加到总列表中
                all_price_data.append({
                    '日期': date,
                    '标题': title,
                    '链接': link,
                    '价格数据': price_data
                })
                
                print(f"成功提取价格数据: {title}")
                
                # 随机延时，避免被封
                random_sleep(3, 6)
                
            except Exception as e:
                print(f"处理文章时出错: {e}")
                continue
    
    except Exception as e:
        print(f"提取过程中出错: {e}")
    
    finally:
        # 关闭浏览器
        driver.quit()
    
    # 将结果保存为JSON文件
    output_file = os.path.join(current_dir, "虾谷订阅号_价格数据.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_price_data, f, ensure_ascii=False, indent=4)
    
    print(f"共提取了 {len(all_price_data)} 篇文章的价格数据，已保存到 {output_file}")
    
    return all_price_data

if __name__ == "__main__":
    extract_price_data()