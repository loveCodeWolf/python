from selenium import webdriver

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
            return curent_url
        elif 'tmall' in current_url:
            print("这是一个天猫商品页面")
            return current_url
    return None

if __name__ == '__main__':
    product_id = 688441876387
    url = detect_url_type(product_id)
    if url:
        print(f"商品页面的URL是: {url}")
    else:
        print("无法确定商品页面的URL")