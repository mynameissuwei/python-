# 克隆自聚宽文章：https://www.joinquant.com/post/33618
# 标题：最简强者恒强策略
# 作者：囚徒

# 克隆自聚宽文章：https://www.joinquant.com/post/33618
# 标题：最简强者恒强策略
# 作者：囚徒

# 导入函数库
from jqdata import *


# 初始化函数，设定基准等等
def initialize(context):
    # 设定基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option("use_real_price", True)

    log.set_level('order', 'error')

    g.target_industries = ['801124', '801120', '801156', '801150']
    g.max_stock_nums = len(g.target_industries)
    g.all_stocks = []

    # 开盘时运行
    run_monthly(market_open, monthday=1, time='open', reference_security='000300.XSHG')
    run_monthly(select_stocks, monthday=1, time='9:00', reference_security='000300.XSHG')


def select4hy(industry):
    # type: (str) -> str
    hys = get_industry_stocks(industry)
    hys = [s for s in hys if s in g.all_stocks]
    stock = get_fundamentals(
        query(
            valuation.code
        ).filter(
            valuation.code.in_(hys)
        ).order_by(
            valuation.market_cap.desc()
        ).limit(
            1
        )
    )['code'][0]
    return stock


def select_stocks(context):
    # type: (Context) -> None
    by_date = context.previous_date - datetime.timedelta(60)
    g.all_stocks = get_all_securities(['stock'], date=by_date).index.tolist()

    stocks = []
    for industry in g.target_industries:
        code = select4hy(industry)
        stocks.append(code)
    #
    g.stocks = stocks
    print(stocks)


def market_open(context):
    # type: (Context) -> None
    for s in context.portfolio.positions:
        if s not in g.stocks:
            order_target(s, 0)

    per_value = context.portfolio.total_value / g.max_stock_nums
    for s in g.stocks:
        order_target_value(s, per_value)
    for s in g.stocks:
        order_target_value(s, per_value)
