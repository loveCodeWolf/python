import hashlib
import re
import requests
import time
import json
import os
from urllib.parse import urlencode


def load_taobao_config():
    """
    从配置文件中加载淘宝配置参数
    :return: 包含_m_h5_tk和Cookie的字典
    """
    config_file = 'taobao_config.json'
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件 {config_file} 不存在，请先创建配置文件")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 检查必要的配置项
        if '_m_h5_tk' not in config:
            raise KeyError("配置文件中缺少 '_m_h5_tk' 参数")
        if 'Cookie' not in config:
            raise KeyError("配置文件中缺少 'Cookie' 参数")
            
        return config
        
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误：{str(e)}")
    except Exception as e:
        raise Exception(f"读取配置文件失败：{str(e)}")


def get_taobao_context(data1,sign1,t1,Cookie):
    """
    :return:
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": Cookie,
    }
    url = f"https://h5api.m.tmall.com/h5/mtop.taobao.rate.detaillist.get/6.0/?jsv=2.7.5&appKey=12574478&api=mtop.taobao.rate.detaillist.get&v=6.0&isSec=0&ecode=1&timeout=20000&type=json&dataType=jsonp&jsonpIncPrefix=pcdetail&callback=mtopjsonppcdetail15&data=%7B%22showTrueCount%22%3Afalse%2C%22auctionNumId%22%3A%22{data1}%22%2C%22pageNo%22%3A1%2C%22pageSize%22%3A20%2C%22rateType%22%3A%22%22%2C%22searchImpr%22%3A%22-8%22%2C%22orderType%22%3A%22%22%2C%22expression%22%3A%22%22%2C%22rateSrc%22%3A%22pc_rate_list%22%7D&sign={sign1}&t={t1}"
    response = requests.get(url, headers=headers)
    # print(response.status_code)
    # print(response)

    # 打印响应内容

    # 使用正则表达式提取 JSON 字符串
    try:
        context = response.json()  # 直接解析 JSON
        rate_list = context['data']['rateList']
        # print(rate_list)

        feedback = ""
        for i in range(30):
            if i < len(rate_list) and rate_list[i].get('rateType') == '1':
                feedback += f"第{i}条评价内容：{rate_list[i]['feedback']},时间：{rate_list[i]['feedbackDate']}\n"
            else:
                break
        return feedback
    except json.JSONDecodeError:
        # print(response.text)
        return "JSON 解析失败，没有评价的响应内容："


def generate_sign(token, data, app_key):
    """
    生成 sign 签名
    :param token: 从 cookie 或其他地方获取的 token 值
    :param data: 请求中的 data 参数 (字典类型)
    :param app_key: 应用的 appKey
    :return: 生成的 sign 值
    """
    # 将 data 转换为字符串格式，这里假设 data 是一个字典
    data_str = json.dumps(data,separators=(',', ':'))


    # 获取当前时间戳
    t = str(int(time.time() * 1000))  # JavaScript 中的时间戳是毫秒级
    # t='1748355453874'

    # 拼接字符串
    string_to_sign = f"{token}&{t}&{app_key}&{data_str}"
    print(string_to_sign)

    # 使用 MD5 生成签名
    sign = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest()
    print(sign)

    return sign,t


def main(Id):
    item_Id = Id
    
    # 从配置文件中读取参数
    try:
        config = load_taobao_config()
        _m_h5_tk = config['_m_h5_tk']
        Cookie = config['Cookie']
    except Exception as e:
        print(f"读取配置失败：{str(e)}")
        # 如果配置文件读取失败，使用默认值（可选）
        _m_h5_tk = 'f7402439e4aabe99dd1565fbb1f02c07'
        Cookie = "thw=cn; useNativeIM=false; wwUserTip=false; wk_cookie2=1a70de4bfc25ec437f4a1c4aa167078b; wk_unb=UUpgQEnfcDI%2FNDbybQ%3D%3D; aui=2216012822830; mt=ci=0_0; cna=fRr9Hkp8Qx8CAXSUuI1YliUD; sgcookie=E100hkNDGSGhs%2BD66vhGirx%2FpwHoe9OnyZ2%2F%2FnIOwaroVvYEUFRAw4bKBg81W0UHC9sjYT8dHS5oNx3V8AfX1W875K24%2B4p%2FTbmQmY5jiCwfdcM%3D; csg=960cab23; lgc=tb861723892; cancelledSubSites=%5B%22xianyu%22%5D; dnk=tb861723892; skt=a86e446dd19e9a62; tracknick=tb861723892; sn=; uc3=nk2=F5RNY%2BrYR%2FKoNnw%3D&vt3=F8dD2f5uhkxR8SJ6DW0%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UUpgQEnfcDI%2FNDbybQ%3D%3D; existShop=MTc0ODcwNzAwMA%3D%3D; uc4=id4=0%40U2gqz6bzdMmbaNBblO42%2BG2uVnsIX2i5&nk4=0%40FY4GtKHkMLjSSJ2QZII0HB3UBwTfzQ%3D%3D; _cc_=VT5L2FSpdA%3D%3D; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=f7402439e4aabe99dd1565fbb1f02c07_1749092566931; _m_h5_tk_enc=460e1311541850951a7f15a388520009; cookie2=197db9ae68b7dc9201c7fe896bb9164c; t=0c5a9f42bb378523e1046397d7699aed; _tb_token_=5e71de31785be; sca=54f5e408; _samesite_flag_=true; 3PcFlag=1749085092336; bxuab=0; x5sectag=501687; x5sec=7b2274223a313734393038353735362c22733b32223a2261613962343465666539343538383534222c22617365727665723b33223a22307c434c6a6367384947454d7561354962382f2f2f2f2f774561447a49794d5459774d5449344d6a49344d7a41374d53494a5932467763485636656d786c4d4c375270717747227d; isg=BH9_CryTK_Yz0yHcLQEkxFcYDlMJZNMGP0bfvhFMhi51IJ6iGTQtVgtzYvDeS6t-; tfstk=gXmZKltSjhKZ3UVTSDZVTFjrZWrTPoRWgmNbnxD0C5Vi5Ssq0WkkB5TvWjuEiXU_sVNf0mPEsias0xI4nxcvBS99RAHTDoAWNo-SBAFYridIbSbhxveVIRYQSd7lFdRWN3tBS9q2_QGXmYOnY-F3I-4gopP33Rq0I-jDLW24eZfiijvUt-eNIi20Iwb3UWV0mocmKpybt-q0mAHT0u13hPvx4LlnvG5Qd7DgTijPeRzMivbfciiTQPlZeWz7PDya774LHWztjXMmfcUpJwZxd4lqobAC550zUXzS7QSZafemTlikHFULomo4p2dVu7umC4308dxiLlPZaDhhnNrZofn4WVWvevqi94F8SedLLci7u7UFtCDIL54rufOdm5grKXzSA6s7q4hE0zql4S1YKiGxDV5cuP2LL79eL774oAnOefaCkZUOdJPWIP7AkP2LL79eLZQYWBwUNd4N."

    with open('sign_data.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
        data = data_list[0].copy()  # 复制一份避免修改原始数据
        data["auctionNumId"] = item_Id  # 修改字段

        print(data)

    sign, t = generate_sign(_m_h5_tk, data, "12574478")

    return get_taobao_context(item_Id, sign, t, Cookie)


if __name__ == '__main__':
    item_Id = '887862383399'
    
    # 从配置文件读取参数
    try:
        config = load_taobao_config()
        _m_h5_tk = config['_m_h5_tk']
    except Exception as e:
        print(f"读取配置失败：{str(e)}")
        _m_h5_tk = 'f7402439e4aabe99dd1565fbb1f02c07'

    # url = "https://h5api.m.tmall.com/h5/mtop.taobao.rate.detaillist.get/6.0/"
    # false  = false
    # print(get_taobao_context(item_Id,url))

    import json

    with open('sign_data.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
        data = data_list[0].copy()  # 复制一份避免修改原始数据
        data["auctionNumId"] = item_Id  # 修改字段

        print(data)

    sign,t = generate_sign(_m_h5_tk, data, "12574478")

    # print(get_taobao_context(item_Id,sign,t))
    print( main(item_Id))