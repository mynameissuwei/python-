from jqdatasdk import *

auth('18817582839', 'Suwei1996728')

target_industries = ['801124', '801120', '801156', '801150']
all_stocks = get_all_securities(['stock'], date='20211206').index.tolist()


def select4hy(industry):
    # type: (str) -> str
    hys = get_industry_stocks(industry)
    hys = [s for s in hys if s in all_stocks]
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


def select_stocks():

    stocks = []
    for industry in target_industries:
        code = select4hy(industry)
        stocks.append(code)
    #
    stocks = stocks
    print(stocks)


select_stocks()

