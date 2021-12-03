# doubleBlow + 折价
import json
import time
import requests
import pandas as pd
import datetime
import wx_send


cookie = 'kbzw__Session=4rif8h52gb6c08dol6kcv2a2q2; kbz_newcookie=1; kbzw_r_uname=%E4%BA%8F%E6%8E%89%E5%BD%A9%E7%A4%BC%E5%8F%98%E5%89%A9%E7%94%B7; kbzw__user_login=7Obd08_P1ebax9aXWxwFRwUAWDUKVwUwXgQBXvUgSQoYmLKg6MLj1Ovo583XyaKa2cPYrKfcl6GYqd7XzN7S2pmvxtmqptvFo5bXsqeaso2yj-vK29XQo5apmKSvrIq0mcyj1L6ixOLyytzN1aiql6mMn6_XxODl5-fU2JyUwuPd3tiXr9fEl8bGmLmQkqTYpp7Yo6CCt9Hn49jPxtKs3e2knqyjpZWsgZ_Cu8yuvI2U5d7U3oy-x9nM5qCTu8ni0OHepKKvmqeQqpetq6GslpC01d_W2-KbrJWtj6qt; Hm_lvt_164fe01b1433a19b507595a43bf58262=1637300441,1637300723; Hm_lpvt_164fe01b1433a19b507595a43bf58262=1637382266'

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.jisilu.cn",
    "Origin": "https://www.jisilu.cn",
    "Referer": "https://www.jisilu.cn/data/cbnew/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": cookie
}


def get_bond_info():
    ts = int(time.time() * 1000)
    url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(ts)
    githubToken = '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'
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


    r = requests.post(
        url=url,
        headers=headers,
        data=data
    )
    ret = r.json()
    result = []
    for item in ret['rows']:
        result.append(item['cell'])
    return result

def ranking(df,condition1='dblow',condition2='curr_iss_amt'):
    NUM = 40
    HoldNum = 10
    df = df.sort_values(by=condition1,ascending=True)[:NUM]
    # print(df,'dff')
    df["curr_iss_amt"] = pd.to_numeric(df["curr_iss_amt"],errors='coerce')
    df = df.sort_values(by=condition2,ascending=True)[:HoldNum]
    return df


def main():
    today = datetime.datetime.now().strftime('%Y%m%d')
    ret = get_bond_info()
    df = pd.DataFrame(ret)
    df = df[['bond_id','bond_nm','premium_rt','price','dblow','curr_iss_amt','increase_rt']]
    filter_data = ranking(df.copy())
    print(filter_data,'filter_data')
    filter_data.to_excel('双低_{}.xlsx'.format(today), encoding='utf8')
    wx_send.wx_send(title='每日双低加规模可转债', content=filter_data)




if __name__ == '__main__':
    main()