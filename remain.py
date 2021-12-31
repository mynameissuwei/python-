# -*- coding: utf-8 -*-
# @File : login.py

import datetime
import time
import pandas as pd
import execjs
import os
import requests
import wx_send
import numpy as np

jsl_user = '17683763005'
jsl_password = 'q1996728'

filename = 'encode_jsl.txt'

path = os.path.dirname(os.path.abspath(__file__))
full_path = os.path.join(path, filename)

headers = {
    'Host': 'www.jisilu.cn', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
    'Cache-Control': 'no-cache', 'Accept': 'application/json,text/javascript,*/*;q=0.01',
    'Origin': 'https://www.jisilu.cn', 'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/67.0.3396.99Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Referer': 'https://www.jisilu.cn/login/',
    'Accept-Encoding': 'gzip,deflate,br',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8'
}


def decoder(text): # 加密用户名和密码
    with open(full_path, 'r', encoding='utf8') as f:
        source = f.read()

    ctx = execjs.compile(source)
    key = '397151C04723421F'
    return ctx.call('jslencode', text, key)


def get_bond_info(session): # 获取行情数据
    ts = int(time.time() * 1000)
    url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(ts)
    data = {
        "fprice": None,
        "tprice": None,
        "curr_iss_amt": None,
        "volume": None,
        "svolume": None,
        "premium_rt": None,
        "ytm_rt": None,
        "rating_cd": None,
        "is_search": "N",
        "btype": "C",
        "listed": "Y",
        "qflag": "N",
        "sw_cd": None,
        "bond_ids": None,
        "rp": 50,
    }

    r = session.post(
        url=url,
        headers=headers,
        data=data
    )
    ret = r.json()
    result = []
    for item in ret['rows']:
        result.append(item['cell'])
    return result


def login(user, password): # 登录
    session = requests.Session()
    url = 'https://www.jisilu.cn/account/ajax/login_process/'
    username = decoder(user)
    jsl_password = decoder(password)
    data = {
        'return_url': 'https://www.jisilu.cn/',
        'user_name': username,
        'password': jsl_password,
        'net_auto_login': '1',
        '_post_type': 'ajax',
    }

    js = session.post(
        url=url,
        headers=headers,
        data=data,
    )

    ret = js.json()

    if ret.get('errno') == 1:
        print('登录成功')
        return session
    else:
        print('登录失败')
        raise ValueError('登录失败')

# 低余额40 低溢价10 
def ranking_low_small(df,condition1='curr_iss_amt',condition2='premium_rt'):
    NUM = 40
    HoldNum = 10
    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    df = df.sort_values(by=condition2,ascending=True)[:HoldNum]
    return df

# 低余额40 低溢价20 双低10 
def ranking_low_small_dblow(df,condition1='curr_iss_amt',condition2='premium_rt',condition3='dblow'):
    NUM = 40
    HoldNum = 20
    BuyNum = 10

    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    df = df.sort_values(by=condition2,ascending=True)[:HoldNum]
    df = df.sort_values(by=condition3,ascending=True)[:BuyNum]
    return df

# 低溢价
def ranking_low(df,condition1='premium_rt'):
    NUM = 10
    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    return df

# 低余额40 双低10
def ranking_dblow_small(df,condition1='curr_iss_amt',condition2='dblow'):
    NUM = 40
    HoldNum = 10
    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    df = df.sort_values(by=condition2,ascending=True)[:HoldNum]
    return df

# 妖债 余额前40 换手率前10
def ranking_remain_turnover(df,condition1='curr_iss_amt',condition2='turnover_rt'):
    NUM = 40
    HoldNum = 10
    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    df = df.sort_values(by=condition2,ascending=False)[:HoldNum]
    return df

# 平价底价溢价率 高价 低溢价 
def ranking_high(df,condition1='price'):
    NUM = 10
    df = df.sort_values(by=condition1,ascending=False)[:NUM]
    return df

def main(): # 主函数
    today = datetime.datetime.now().strftime('%Y%m%d')
    session = login(jsl_user, jsl_password)
    ret = get_bond_info(session)
    df = pd.DataFrame(ret)
    df = df[['bond_id','bond_nm','premium_rt','price','dblow','curr_iss_amt','increase_rt','turnover_rt']]
    df["price"] = pd.to_numeric(df["price"],errors='coerce')
    df["turnover_rt"] = pd.to_numeric(df["turnover_rt"],errors='coerce')
    df['premium_rt'] = df['premium_rt'].str.replace(r'%', '', regex=True)
    df["premium_rt"] = pd.to_numeric(df["premium_rt"],errors='coerce')
    writer = pd.ExcelWriter('jsl_{}.xlsx'.format(today))
    
    filter_low_small_data = ranking_low_small(df.copy())
    filter_low_data = ranking_low(df.copy())
    filter_dblow_remain_data = ranking_dblow_small(df.copy())
    filter_remain_turnover_data = ranking_remain_turnover(df.copy())
    filter_high_data = ranking_high(df.copy())
    filter_dblow_remain_low_data = ranking_low_small_dblow(df.copy())

    filter_low_data.to_excel(writer,'低溢价')
    filter_low_small_data.to_excel(writer,'低余额40 低溢价10')
    filter_dblow_remain_data.to_excel(writer,'低余额40 双低10')
    filter_dblow_remain_low_data.to_excel(writer,'低余额40 低溢价20 双低10')
    filter_remain_turnover_data.to_excel(writer,'低余额前40 换手率前10')
    filter_high_data.to_excel(writer,'平价底价溢价率 高价10 低溢价')




    # resultString = ' '.join(list(filter_data['bond_nm']))
    # wx_send.wx_send(title='双低加规模', content=resultString)
    try:
        writer.save()
    except Exception as e:
        print(e)
    else:
        print('导出excel成功')


if __name__ == '__main__':
    main()

