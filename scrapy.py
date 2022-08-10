# -*- coding: utf-8 -*-
# @File : login.py

import datetime
import time
import pandas as pd
import execjs
import os
import requests

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
    url = 'https://www.jisilu.cn/data/cbnew/cb_list_new/?___jsl=LST___t={}'.format(ts)
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


def main(): # 主函数
    today = datetime.datetime.now().strftime('%Y%m%d')
    session = login(jsl_user, jsl_password)
    ret = get_bond_info(session)
    df = pd.DataFrame(ret)
    try:
        df.to_excel('jsl_{}.xlsx'.format(today), encoding='utf8')
    except Exception as e:
        print(e)
    else:
        print('导出excel成功')


if __name__ == '__main__':
    main()
