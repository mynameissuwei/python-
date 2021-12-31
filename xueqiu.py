# 自动同步券商持仓到雪球的组合

import pandas as pd
import json
import requests
import warnings

warnings.filterwarnings("ignore")

cookie = '你的cookie'
gid = '你的gid'
filename='例子.xlsx'

def trade_record(cookie, data):
    url = 'https://tc.xueqiu.com/tc/snowx/MONI/transaction/add.json'

    header = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-length': '104',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie,
        'origin': 'https://xueqiu.com',
        'referer': 'https://xueqiu.com/performance',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    resp = requests.post(url, data=data, headers=header, verify=False)
    content = resp.content.decode(resp.encoding)

    data_dict = json.loads(content)
    success = data_dict['success']

    name = data_dict['result_data']['name']
    price = data_dict['result_data']['price']
    direction = "卖出" if data_dict['result_data']['type'] == 2 else "买入"

    shares = data_dict['result_data']['shares']
    msg = data_dict['msg']
    # print(data_dict)
    print("{}：以 {} {} {}，{}".format(name, price, direction, shares, msg))
    return success


def history_trade(se, cookie, tableid):
    trade_type = '2' if se['委托类别'] == '卖出' else '1'
    tradedate = str(se['成交日期'])

    date = '{}-{}-{}'.format(tradedate[:4], tradedate[4:6], tradedate[6:8])
    symbol = 'SH' if se['股东代码'][0] == 'A' else 'SZ'
    symbol += str(se['证券代码'])
    price = se['成交价格']
    shares = se['成交数量'] * 10 if se['股东代码'][0] == 'A' else se['成交数量']

    commission = se['佣金']

    data = {
        'type': trade_type,  # 1 买入 2 卖出
        'date': date,
        'gid': tableid,
        'symbol': symbol,
        'price': price,
        'shares': shares,
        'commission': commission
    }
    success = trade_record(cookie, data)
    return data


def main():


    history_trade_info_df = pd.read_excel(filename)

    print(history_trade_info_df.head())
    history_trade_info_df['success'] = history_trade_info_df.apply(lambda x: history_trade(x, cookie, gid), axis=1)
    print("失败个数：{}".format(len(history_trade_info_df[history_trade_info_df['success'] == False])))
    print(history_trade_info_df[history_trade_info_df['success'] == False])


if __name__ == '__main__':
    main()