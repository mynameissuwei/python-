# doubleBlow + 折价
import json
import time
import requests
import pandas as pd
import datetime
import wx_send


cookie = '7eb3b26f-38aa-4a36-ba00-5dca63f9002a'

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "ww2.ezhai.net.cn",
    "Origin": "https://ww2.ezhai.net.cn",
    "Referer": "https://ww2.ezhai.net.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "token": cookie
}

double_blow_string = ''

def get_bond_info():
    ts = int(time.time() * 1000)
    url = 'https://api1.ezhai.net.cn/ezhai/getAllData'
    # githubToken = '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'
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


    r = requests.get(
        url=url,
        headers=headers,
        # data=data
    )
    print(r,'rrrr')


def main():
    ret = get_bond_info()
    print(ret,'ret')







if __name__ == '__main__':
    main()