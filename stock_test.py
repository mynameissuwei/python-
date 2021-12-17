from jqdatasdk import *
import datetime

auth('18817582839', 'Suwei1996728')


def get_stock_list():
    """
    获取所有A股股票列表
    上海证券交易所.XSHG
    深圳证券交易所.XSHE
    :return: stock_list
    """
    stock_list = list(get_all_securities(['stock']).index)
    return stock_list


def get_stock_amplitude():
    """
    获取振幅数据
    """
    end_date = datetime.datetime.today()
    stock_list = list(get_all_securities(['stock']).index)
    df = get_price(stock_list, end_date=end_date, fields=['low', 'pre_close', 'high'], count=1, frequency='1d',
                   skip_paused=False, fq='pre')
    df['amplitude'] = (df.high - df.low) / df.pre_close
    df = df.sort_values(by='amplitude',ascending=False)[:20]
    print(df,'df')


def get_index_list(index_symbol='399997.XSHE'):
    """
    获取指数成分股，指数代码查询：https://www.joinquant.com/indexData
    :param index_symbol: 指数的代码，默认沪深300
    :return: list，成分股代码
    """
    stocks = get_index_stocks(index_symbol)
    return stocks


def get_single_price(code, time_freq, start_date=None, end_date=None):
    """
    获取单个股票行情数据
    :param code:
    :param time_freq:
    :param start_date:
    :param end_date:
    :return:
    """
    # 如果start_date=None，默认为从上市日期开始
    if start_date is None:
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    # 获取行情数据
    data = get_price(code, start_date=start_date, end_date=end_date,
                     frequency=time_freq, panel=False)  # 获取获得在2015年
    return data


if __name__ == '__main__':
    print(get_stock_amplitude())
