from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import time

def parse_cookies(cookie_str, domain='.taobao.com'):
    """
    将 Cookie 字符串解析为字典列表
    :param cookie_str: Cookie 字符串
    :return: 字典形式的 Cookie 列表
    """
    cookies = []
    for item in cookie_str.split("; "):
        if "=" in item:
            name, value = item.split("=", 1)
            cookies.append({
                'name': name,
                'value': value,
                'domain': domain,  # 设置正确的域名
                'path': '/'  # 默认路径
            })
        else:
            # 忽略无效的 Cookie 格式
            continue
    return cookies

def extract_product_info(page_source):
    """
    从页面源码中提取商品信息
    :param page_source: 页面HTML源码
    :return: 商品信息字典
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    
    product_info = {
        'name': '',
        'parameters': [],
        'colors': [],
        'guarantees': [],
        'price': '',
        'color_stock_info': []  # 新增：颜色和库存信息
    }
    
    try:
        # 提取商品名称
        # 尝试多种可能的选择器
        name_selectors = [
            'h1[data-spm="1000983"]',
            '.tb-detail-hd h1',
            'h1.tb-item-title',
            '.item-title h1',
            'h1',
            '[data-spm="1000983"]'
        ]
        
        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                product_info['name'] = name_element.get_text().strip()
                break
        
        # 如果还是没找到，尝试从页面标题获取
        if not product_info['name']:
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text().strip()
                # 移除常见的后缀
                title_text = re.sub(r'[-_].*?(tmall|taobao|天猫|淘宝).*$', '', title_text, flags=re.IGNORECASE)
                product_info['name'] = title_text
        
        # 提取商品价格
        price_selectors = [
            '.esVfqSHIbS--priceText--_8548974',  # 根据您提供的HTML结构
            '.esVfqSHIbS--MiniPrice--a248cc80 .esVfqSHIbS--priceText--_8548974',
            '[class*="priceText"]',
            '[class*="price"] span',
            '.tb-rmb-num',
            '.tm-price-panel .tm-price'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                if price_text and price_text.replace('.', '').isdigit():
                    product_info['price'] = f"¥{price_text}"
                    break
        
        # 提取参数信息（根据您提供的HTML结构）
        # 首先尝试新的参数信息结构
        param_container = soup.select_one('[data-tabindex="1"] .esVfqSHIbS--tableWrapper--adb69e24')
        if param_container:
            param_items = param_container.select('.esVfqSHIbS--infoItem--_6d170e8')
            for item in param_items:
                title_elem = item.select_one('.esVfqSHIbS--infoItemTitle--_1ce349f')
                content_elem = item.select_one('.esVfqSHIbS--infoItemContent--f2042d56')
                if title_elem and content_elem:
                    title = title_elem.get_text().strip()
                    content = content_elem.get_text().strip()
                    if title and content:
                        product_info['parameters'].append(f"{title}: {content}")
        
        # 如果没找到，尝试原有的选择器
        if not product_info['parameters']:
            param_selectors = [
                '.tb-property-cont table tr',
                '.attributes-list li',
                '.tb-detail-prop li',
                '.item-props li',
                '[class*="param"] li',
                '[class*="property"] tr'
            ]
            
            for selector in param_selectors:
                param_elements = soup.select(selector)
                if param_elements:
                    for element in param_elements:
                        text = element.get_text().strip()
                        if text and ':' in text:
                            product_info['parameters'].append(text)
                    break
        
        # 提取颜色分类和库存信息（根据您提供的HTML结构）
        sku_container = soup.select_one('.esVfqSHIbS--skuItem--_68c0cae')
        if sku_container:
            # 检查是否是颜色分类
            label_elem = sku_container.select_one('.esVfqSHIbS--labelText--_2ce831b')
            if label_elem and '颜色分类' in label_elem.get_text():
                color_items = sku_container.select('.esVfqSHIbS--valueItem--ee898cc0')
                for item in color_items:
                    color_text_elem = item.select_one('.esVfqSHIbS--valueItemText--f5b4bd44')
                    if color_text_elem:
                        color_name = color_text_elem.get('title') or color_text_elem.get_text().strip()
                        if color_name:
                            # 检查是否选中（当前价格对应的颜色）
                            is_selected = 'esVfqSHIbS--isSelected--be9dcb21' in item.get('class', [])
                            
                            color_info = {
                                'color': color_name,
                                'is_selected': is_selected,
                                'stock_status': '有货'  # 默认有货，可以根据实际情况调整
                            }
                            
                            product_info['color_stock_info'].append(color_info)
                            product_info['colors'].append(color_name)
        
        # 检查库存状态
        stock_tip = soup.select_one('.esVfqSHIbS--quantityTip--_7871329')
        if stock_tip:
            stock_status = stock_tip.get_text().strip()
            # 更新当前选中颜色的库存状态
            for color_info in product_info['color_stock_info']:
                if color_info['is_selected']:
                    color_info['stock_status'] = stock_status
                    break
        
        # 如果没有找到颜色信息，尝试原有的选择器
        if not product_info['colors']:
            color_selectors = [
                '[data-property="颜色分类"] li',
                '[data-property="color"] li',
                '.tb-sku-color li',
                '.sku-color-list li',
                '[class*="color"] li a',
                '[class*="sku"] li[title]'
            ]
            
            for selector in color_selectors:
                color_elements = soup.select(selector)
                if color_elements:
                    for element in color_elements:
                        # 尝试获取title属性或文本内容
                        color_text = element.get('title') or element.get_text().strip()
                        if color_text and color_text not in product_info['colors']:
                            product_info['colors'].append(color_text)
                    break
        
        # 提取保障信息
        guarantee_selectors = [
            '.tb-service li',
            '.service-list li',
            '.guarantee-list li',
            '[class*="service"] li',
            '[class*="guarantee"] li',
            '.tb-detail-service li'
        ]
        
        for selector in guarantee_selectors:
            guarantee_elements = soup.select(selector)
            if guarantee_elements:
                for element in guarantee_elements:
                    text = element.get_text().strip()
                    if text and len(text) > 2:  # 过滤太短的文本
                        product_info['guarantees'].append(text)
                break
        
        # 如果没有找到保障信息，尝试查找包含关键词的文本
        if not product_info['guarantees']:
            guarantee_keywords = ['保障', '服务', '退换', '质保', '包邮', '正品']
            all_text_elements = soup.find_all(text=True)
            for text in all_text_elements:
                text = text.strip()
                if any(keyword in text for keyword in guarantee_keywords) and len(text) < 50:
                    product_info['guarantees'].append(text)
                    if len(product_info['guarantees']) >= 5:  # 限制数量
                        break
    
    except Exception as e:
        print(f"提取商品信息时出错: {e}")
    
    return product_info

def format_product_info(product_info):
    """
    将商品信息格式化为一段话
    :param product_info: 商品信息字典
    :return: 格式化的商品描述
    """
    description_parts = []
    
    # 商品名称
    if product_info['name']:
        description_parts.append(f"商品名称：{product_info['name']}")
    
    # 商品价格
    if product_info['price']:
        description_parts.append(f"商品价格：{product_info['price']}")
    
    # 参数信息
    if product_info['parameters']:
        # params_text = "；".join(product_info['parameters'][:5])  # 限制显示前5个参数
        params_text = "；".join(product_info['parameters']) 
        description_parts.append(f"主要参数：{params_text}")
    
    # 颜色分类和库存信息
    if product_info['color_stock_info']:
        color_stock_details = []
        for color_info in product_info['color_stock_info']:  # 限制显示前8种颜色
            status_mark = "(当前选中)" if color_info['is_selected'] else ""
            color_stock_details.append(f"{color_info['color']}{status_mark}[{color_info['stock_status']}]")
        colors_text = "、".join(color_stock_details)
        description_parts.append(f"可选颜色及库存：{colors_text}")
    elif product_info['colors']:
        colors_text = "、".join(product_info['colors'])  # 限制显示前8种颜色
        description_parts.append(f"可选颜色：{colors_text}")
    
    # 保障信息
    if product_info['guarantees']:
        guarantees_text = "、".join(product_info['guarantees'])  # 限制显示前5个保障
        description_parts.append(f"服务保障：{guarantees_text}")
    
    # 组合成完整描述
    if description_parts:
        return "。".join(description_parts) + "。"
    else:
        return "未能提取到完整的商品信息，请检查页面加载情况。"

def get_taobao_index_2(item_id):
    # 初始化浏览器驱动
    driver = webdriver.Chrome()
    
    try:
        # Cookie 字符串
        cookie_str = (
            "cna=fRr9Hkp8Qx8CAXSUuI1YliUD; lid=tb861723892; wk_cookie2=1a70de4bfc25ec437f4a1c4aa167078b; "
            "wk_unb=UUpgQEnfcDI%2FNDbybQ%3D%3D; isg=BGBg1v7MHJi7bq7RpuWHwSAcMW4yaUQzNLOQc9pxfXsO1QH_gnlEw82mbH3V1_wL; "
            "dnk=tb861723892; uc3=nk2=F5RNY%2BrYR%2FKoNnw%3D&vt3=F8dD2f5uhkxR8SJ6DW0%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UUpgQEnfcDI%2FNDbybQ%3D%3D; "
            "tracknick=tb861723892; _l_g_=Ug%3D%3D; uc4=id4=0%40U2gqz6bzdMmbaNBblO42%2BG2uVnsIX2i5&nk4=0%40FY4GtKHkMLjSSJ2QZII0HB3UBwTfzQ%3D%3D; "
            "unb=2216012822830; lgc=tb861723892; cookie1=BdXaGwX5FYr9EilKa1ygYIMObpuC5CxykEOqe2LbnNM%3D; login=true; "
            "cookie17=UUpgQEnfcDI%2FNDbybQ%3D%3D; cookie2=298aef1300907fbc12d72f5cca9fbcaf; _nk_=tb861723892; "
            "sgcookie=E100hkNDGSGhs%2BD66vhGirx%2FpwHoe9OnyZ2%2F%2FnIOwaroVvYEUFRAw4bKBg81W0UHC9sjYT8dHS5oNx3V8AfX1W875K24%2B4p%2FTbmQmY5jiCwfdcM%3D; "
            "cancelledSubSites=%5B%22xianyu%22%5D; t=3bb20e02982fbd08f39cff1053cad1b1; sg=20b; csg=960cab23; sn=; _tb_token_=e8363e7173338; "
            "bxuab=0; mtop_partitioned_detect=1; _m_h5_tk=325b06bbeec91b2744ca35bdaab0fa48_1749022397982; _m_h5_tk_enc=71d4ff05e360b7b3c3bfac3a398268c6; "
            "tfstk=gsqrQYj_qgIPdJh-roiegLV76Ti-RD51UkGIKJ2nFbcl9THnY7Nm-Hw5y9WEgWhSP04SKHPjGWtQFkzvYReLVTnCe0e-vDf11GiUe8nLJRVbPswcKvnEELg5bC2-vDfXhHb1b8F-HdHUEDXqmvkeqDcoEKXqdA-nxb0HiEDiiDmnZ4AmivH6qUxoKtymMvmntW0l3qcxKb--YcOmd4XLYlim-acjzf2ogH270Y0yy8c2xHq4T4lM1j-HxokzHQscJh7IsPhS5fFcc3oUnvPq5z5w4Wy3By04YQX7sJV800nNRT3aoraszr5kYjZSLVmnupx338cb_umGjIkYo8a327JexYE7f2ltu9xKRmqsSPVypOemqvVKWk192b23BlUsbgRtUr2Z0gl29xxQ9kUyteuoHxl13tlw8228Tt0WfeLKyKMq1T0yJe3oHxl13t8pJ4Cj3f6oz"
        )
        
        # 打开目标网址（必须先访问该域名，才能设置 Cookie）818020021783，688441876387，  780810309350
        # url = 'https://item.taobao.com/item.htm?id=780810309350'
        url,domain = detect_url_type(item_id)

        # 解析 Cookie 字符串
        cookies = parse_cookies(cookie_str,domain)

        driver.get(url)
        
        # 删除默认的 Cookie
        driver.delete_all_cookies()
        
        # 添加自定义 Cookie
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"添加Cookie失败: {cookie['name']}, 错误: {e}")
        
        # 重新加载页面以应用 Cookie
        driver.refresh()
        
        # 等待页面加载完成
        time.sleep(3)
        
        # 获取页面内容
        page_source = driver.page_source
        # print(page_source)
        
        # 提取商品信息
        print("正在提取商品信息...")
        product_info = extract_product_info(page_source)
        
        # 格式化输出
        formatted_description = format_product_info(product_info)
        
        print("\n=== 商品信息提取结果 ===")
        print(f"商品名称: {product_info['name']}")
        print(f"商品价格: {product_info['price']}")
        print(f"参数信息: {product_info['parameters'][:3] if product_info['parameters'] else '未找到'}")
        print(f"颜色分类: {product_info['colors'][:5] if product_info['colors'] else '未找到'}")
        print(f"颜色库存详情: {product_info['color_stock_info'][:3] if product_info['color_stock_info'] else '未找到'}")
        print(f"保障信息: {product_info['guarantees'][:3] if product_info['guarantees'] else '未找到'}")
        
        print("\n=== 格式化商品描述 ===")
        print(formatted_description)
        
        return {
            'raw_info': product_info,
            'formatted_description': formatted_description
        }
        
    except Exception as e:
        print(f"爬取过程中出错: {e}")
        return None
    
    finally:
        # 关闭浏览器
        driver.quit()
#进行检测区分到底是淘宝还是天猫的链接
def detect_url_type(product_id):
    driver = webdriver.Chrome()
    urls = [
        f'https://item.taobao.com/item.htm?id={product_id}',
        f'https://detail.tmall.com/item.htm?id={product_id}'
    ]

    for url in urls:
        driver.get(url)
        current_url = driver.current_url
        if 'taobao' in current_url:
            print("这是一个淘宝商品页面")
            return current_url, '.taobao.com'
        elif 'tmall' in current_url:
            print("这是一个天猫商品页面")
            return current_url, '.tmall.com'
    driver.quit()  # 建议添加：确保浏览器关闭
    return None


if __name__ == '__main__':
    result = get_taobao_index_2(780810309350)
    if result:
        print("\n爬取完成！")
    else:
        print("\n爬取失败！")
