# 克隆自聚宽文章：https://www.joinquant.com/post/28782
# 标题：小资金短线策略
# 作者：rickch

# 代码不长，稍稍研究了一下，楼主的思路如下：
# 取30个1min的‘close’数据，计算出两个参数
# 参数1：乖离率bias，即最近的‘close’/12分钟均线值-1。能够体现股价偏离12分钟均线的情况
# 参数2：近30min的涨跌幅ret，即当前的股价/30min之前的股价 -1。能体现股价最近的涨跌情况

# 最后将两个参数相加，取数值最小的第2-第5只股票（原因楼主已说明）。
# 开盘买入，次日卖出。

# 从胜率来看，接近0.5，但是上涨的平均幅度大于下跌的平均幅度，所以收益这么可观。
# 用的是history来提取数据，而且是开盘前决策，开盘后只进行买卖， 应该是没有未来函数的。
# 感觉可以深入研究一下。比如优化一下universe或者买卖仓位和时间控制。
# 我用聚宽已经2年了，还没搞出自己的策略，实在是头疼且没有思路，写了这么多，希望楼主看到能够指点一二。

'''
1、计算尾盘半小时收益率
2.计算尾盘半小时乖离率
3.合并两个因子排序选股
'''
import numpy as numpy
import pandas as pd


def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000905.XSHG')
    # True为开启动态复权模式，使用真实价格交易
    set_option('use_real_price', True)
    # 设定成交量比例
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5),
                   type='stock')
    # 设定成交占比，避免价格冲击
    set_option('order_volume_ratio', 0.25)
    # 开盘价成交，理论上无滑点
    set_slippage(FixedSlippage(0))
    # 最大建仓数量
    g.max_hold_stocknum = 3
    # 运行函数
    run_daily(before_trading_start, time='09:00')
    run_daily(trade, time='9:30')


## 获取 购买标的
def before_trading_start(context):
    t_date = context.current_dt.strftime('%Y-%m-%d')
    # p_date = context.previous_date.strftime ('%Y-%m-%d')   没用上
    # 可选沪深300，中证500，中证800，不宜用成交不活跃的指数
    universe = get_index_stocks('000905.XSHG', date=t_date)
    universe = get_feasible(universe)
    # set_universe (universe)
    data = history(30, unit='1m', field='close', security_list=universe, df=True, skip_paused=True, fq=None)
    bias = data.apply(lambda x: get_bias(x))
    data = data / data.iloc[0, :] - 1
    ret = data.iloc[-1, :].T
    factor = pd.concat([bias, ret], axis=1)
    factor['sum'] = factor.sum(axis=1)
    # 跑过实盘，选中间的3-5只较好，排名最前的股票往往由于基本面问题下跌，反转效应不强
    g.security = list(factor.sort_values('sum').iloc[2:5].index)


## 交易函数
def trade(context):
    for security in context.portfolio.long_positions:
        # 全部卖出
        order_target(security, 0)
        # 记录这次卖出
    # log.info("Selling %s" % (context.portfolio.long_positions))

    for security in g.security:
        value = context.portfolio.available_cash / 3  # 资金分成三份
        order_value(security, value, side='long')
    # log.info ("buying %s" % (g.security))


## 计算乖离率
def get_bias(series):
    average = np.array(series.rolling(window=12).mean())
    Y = series.iloc[-1] / average[-1] - 1
    return Y


## 剔除st和停牌
def get_feasible(universe):
    curr_data = get_current_data()
    stocks = [stock for stock in universe if
              (not curr_data[stock].paused) and (not curr_data[stock].is_st) and ('ST' not in curr_data[stock].name) \
              and ('*' not in curr_data[stock].name) and ('退' not in curr_data[stock].name)]
    return stocks
##def after_trading_end (context):

