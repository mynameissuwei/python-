# 第一步

start_date = '2021-01-01'  # 回测起始时间
end_date = '2022-01-01'  # 回测结束时间

def get_last_trading_day():
    df = DataAPI.TradeCalGet(exchangeCD=u"XSHG,XSHE",beginDate=start_date,endDate=end_date,isOpen=u"1",field=u"calendarDate,prevTradeDate",pandas="1")
    df['calendarDate']=df['calendarDate'].map(lambda x:x.replace('-',''))
    df['prevTradeDate']=df['prevTradeDate'].map(lambda x:x.replace('-',''))
    return dict(zip(df.loc[:,'calendarDate'],df.loc[:,'prevTradeDate']))

canlender_dict = get_last_trading_day()



import datetime
import numpy as np
import copy
import pandas as pd
import datetime
MAX = np.inf
extra_num = 0
start = start_date
end = end_date
benchmark = 'HS300'                        # 策略参考标准
freq = 'd'  
rotation_rate = 5 # 调仓频率 调仓频率，表示执行handle_data的时间间隔，若freq = 'd' 时间间隔的单位为交易日，取盘前数据，若freq = 'm' 时间间隔为分钟
current_day =0       
refresh_rate = 1# 
hold_num = 10 # 持有转债的个数
current_day =0
history_profit=[]
daily_netvalue =[]
holding_list=[]
ratation_list=[]
EB_ENABLE=False
force_redemption_dict = {}

Remain_Factor = 1
DoubleLow_Factor = 9

REMAIN_SIZE = 5 # 5亿

def formator():
    print('='*20)
    print('\n')
    
def initialize(context):
    global MyPosition, HighValue, MyCash, Withdraw, HoldRank, HoldNum,Start_Cash
    MyPosition = {}  #持仓
    MyCash = 100000000  #现金
    Start_Cash= 100000000
    HighValue = MyCash  #最高市值
    Withdraw = 0  #最大回撤
    HoldRank = hold_num  #排名多少之后卖出
    HoldNum = hold_num  #持债支数
    
    print("{} 启动".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%SS")))
    
def get_bonds_list(beginDate=u"20170101", endDate=u"20201215"):
    df = DataAPI.MktConsBondPremiumGet(SecID=u"",
                                       tickerBond=u"",
                                       beginDate=beginDate,
                                       endDate=endDate,
                                       field=u"",
                                       pandas="1")

    cb_df = df.tickerBond.str.startswith(('12', '11'))
    df = df[cb_df]
    cb_df = df.tickerBond.str.startswith('117')
    df = df[~cb_df]
    if not EB_ENABLE:
        eb = df.secShortNameBond.str.match('\d\d.*?E[123B]')  # TODO 判断EB是否过滤
        df = df[~eb]

    ticker_list = []
    remove_duplicated = set()
    for _, row in df[['tickerBond', 'secShortNameBond', 'tickerEqu']].iterrows():
        if row['tickerBond'] not in remove_duplicated:
            ticker_list.append((row['tickerBond'], row['secShortNameBond'], row['tickerEqu']))
            remove_duplicated.add(row['tickerBond'])
    ticker_list = force_redemption(ticker_list, beginDate)
    return ticker_list

def get_last_price(code, start_date, last_data):
    bond_info_df = DataAPI.MktBonddGet(secID=u"", 
                                       ticker=code,
                                       tradeDate=u"",
                                       beginDate=start_date,
                                       endDate=last_data,
                                       field=u"closePrice",
                                       pandas="1")
    if len(bond_info_df) > 0:
        price = round(bond_info_df['closePrice'].iloc[-1], 2)
    else:
        print(code)
        raise ValueError('查询last price 失效, {}'.format(code))
    return price


# ---------------强赎 ----------------
def force_redemption(ticker_list, today):
    global force_redemption_dict,canlender_dict
    ticker_list_code = []
    for item in ticker_list:
        if item[0] not in force_redemption_dict:
            ticker_list_code.append(item[0])

    df = DataAPI.BondConvStockItemGet(secID=u"",
                                      ticker=ticker_list_code,
                                      bondID=u"",
                                      convID=u"",
                                      field=u"ticker,traStoptime",
                                      pandas="1")

    df = df[~df['traStoptime'].isnull()]
    if len(df) > 0:
        df['traStoptime']=df['traStoptime'].map(lambda x:x.replace('-',''))
        new_force_redemption_notice = dict(zip(df['ticker'].tolist(), df['traStoptime'].tolist()))
        force_redemption_dict.update(new_force_redemption_notice)
    new_list_data = copy.deepcopy(ticker_list)

    for _ticker in new_list_data:
        force_redemption_date = force_redemption_dict.get(_ticker[0],None)         
        if force_redemption_date is not None:
            last_day_force_ = canlender_dict.get(force_redemption_date,None)
            if last_day_force_ is not None and last_day_force_ <= today:
                log.info('强赎日 {}移除强赎债 {}, {}今日日期{},------强赎前一天的日期{}'.format(force_redemption_date,_ticker[0],_ticker[1],today,last_day_force_))
                ticker_list.remove(_ticker)

    print('\n')
    return ticker_list


def get_position_netvalue(today_date):
    global PosValue,MyCash,HighValue,Withdraw,Start_Cash,daily_netvalue,holding_list
    ticker_list = list(MyPosition.keys())
    if len(ticker_list)==0:
        print('{}没有持仓'.format(today_date))
        return 
    
    data = DataAPI.MktConsBondPerfGet(
        beginDate=today_date,
        endDate=today_date,
        secID='',
        tickerBond=ticker_list, 
        tickerEqu=u"",
        field=u"tickerBond,closePriceBond,bondPremRatio,secShortNameBond,tickerEqu,remainSize,chgPct",
        pandas="1"
    )
    
    if len(data)==0:
        print('数据为空')
        return
    
    data=data.set_index('tickerBond',drop=False)
    last_post = PosValue
    PosValue = MyCash
    for ticker in ticker_list:
        try:
            closePriceBond = data.loc[ticker,'closePriceBond']

        except Exception as e:
            # print(e)
            # print('日更新 没有查询到价格,ticker {} 强赎了吗？'.format(ticker))
            today_parse = datetime.datetime.strptime(today_date,'%Y%m%d')
            start_date = (today_parse + datetime.timedelta(days=-14)).strftime('%Y%m%d')
            closePriceBond=get_last_price(ticker,start_date, today_date)
        
        bond_pos = MyPosition[ticker]*closePriceBond*10
        PosValue+=bond_pos
    today_pct = (PosValue-last_post)/last_post * 100
    # log.info('当日收益率 {}'.format(today_pct))
    if PosValue > HighValue: HighValue = PosValue
    if (HighValue - PosValue) / HighValue > Withdraw: Withdraw = (HighValue - PosValue) / HighValue
    ratio = round((PosValue - Start_Cash) / Start_Cash * 100,2)
    
    
    message = today_date + ': 最高市值 ' + str(HighValue) + ' , 当前市值 ' + str(PosValue) + '收益率 ： ' + str(ratio) + '% , 最大回撤 ' + str(round(Withdraw * 100, 2)) + '%' + ' 当日收益率:'+str(today_pct)
    # log.info('当前持仓')
    # log.info(MyPosition)
    # log.info(message)
    
    df=data[data['tickerBond'].isin(ticker_list)]
    df=df.reset_index(drop=True)
    df['tradeDate']=today_date
    holding_list.append(df)
    daily_netvalue.append({'日期':today_date,'当前市值':PosValue,'收益率':ratio,'最大回撤':round(Withdraw * 100, 2),'daily_profit':today_pct})

# ==================================================================================================
    
    
def ranking(df,condition1='remainSize'):
    '''
    组装排名
    '''
    'remainSize'
    'doublelow'
    NUM = 40 # 40个里面选
    df = df.sort_values(by=condition1,ascending=True)[:HoldNum]
    return df
    
def handle_data(context):    

    global MyPosition, HighValue, MyCash, Withdraw, HoldRank, HoldNum, Start_Cash, threshold,history_profit,current_day,holding_list,daily_netvalue,ratation_list,PosValue
    previous_date = context.previous_date.strftime('%Y%m%d')
    today_date = context.now.strftime('%Y%m%d')

    if current_day%rotation_rate!=0:
        get_position_netvalue(today_date)
        current_day = current_day + 1
        return
    
    bonds_list = get_bonds_list(beginDate=today_date, endDate=today_date)

    if len(bonds_list) == 0:
        log.info('没有符合条件的转债')
        return

    ticker_dict = {}
    for ticker, name, ticker_zg in bonds_list:
        tmp_dict = {}
        ticker_dict[ticker] = {'name': name, 'zg': ticker_zg}

    ticker_list = list(ticker_dict.keys())
    
    data = DataAPI.MktConsBondPerfGet(
        beginDate=today_date,
        endDate=today_date,
        secID='',
        tickerBond=ticker_list, 
        tickerEqu=u"",
        # field=u'',
        field=u"tickerBond,closePriceBond,bondPremRatio,secShortNameBond,tickerEqu,remainSize,chgPct",
        pandas="1")
    

    
    data['doublelow'] = data['closePriceBond'] * 0.8 + data['bondPremRatio'] * 1.2
    
    condition = "closePriceBond" # 条件
    # data = data[data['remainSize']<REMAIN_SIZE]
    
    filter_data = ranking(data.copy(),condition1='remainSize')
    last_bond_list = filter_data['tickerBond'].tolist()
    
    filter_data.set_index('tickerBond',inplace=True)
    
    data['secID'] = data['tickerBond']
    
    data.set_index('secID', inplace=True)
    # data = data.sort_values(by=condition , ascending=True)
    temp_df=data[:HoldNum + extra_num].copy()
    temp_df['tradeDate']=today_date
    ratation_list.append(temp_df)
    
    PosValue = MyCash
    
    for stock in MyPosition.keys():
        try:
            CurPrice = data.loc[stock]['closePriceBond']
        except Exception as e:

            last_date = (context.now + datetime.timedelta(days=-14)).strftime('%Y%m%d')
            CurPrice = get_last_price(stock, last_date, today_date)


        PosValue += MyPosition[stock] * CurPrice * 10  # 计算当前市值

        if stock not in last_bond_list:
            MyCash += MyPosition[stock] * CurPrice * 10
            online = True
            
            try:
                name_ = data.loc[stock]['secShortNameBond']
                chgPct = data.loc[stock]['chgPct']*100
            except:
                name_ = stock
                online =False
            
            if online:
                cb_ration = data.loc[stock]['bondPremRatio']
            else:
                cb_ration=''
                chgPct=''
                
            message ='{} 卖出{}, {}, 价格 {}, 溢价率 {}, 当日涨幅{}'.format(today_date, stock, name_, CurPrice,
                                                                                cb_ration,chgPct)
            log.info(message)
            
            history_profit.append(message)
            
            del MyPosition[stock]
    
    if PosValue > HighValue: HighValue = PosValue
    if (HighValue - PosValue) / HighValue > Withdraw: Withdraw = (HighValue - PosValue) / HighValue
    
    min_hold = min(HoldNum,len(data.index))
    
    for i in range(min_hold):
        if len(MyPosition) == HoldNum:break
        
        # 买入排在HoldRank内的，总持有数量HoldNum
        code_ = filter_data.index[i] 
        if code_ not in MyPosition.keys():
            name = filter_data.loc[code_]['secShortNameBond']
            price = filter_data.loc[code_]['closePriceBond']
            cb_ration = filter_data.loc[code_]['bondPremRatio']
            # rank = filter_data.loc[code]['final_rank']
            chgPct = filter_data.loc[code_]['chgPct']*100
            
            message ='{} 买入{}, {}, 价格 {}, 溢价率 {}, 当日涨幅{}'.format(today_date, code_, name, price,
                                                                                cb_ration,chgPct,)
            log.info(message)
            history_profit.append(message)
            
            MyPosition[code_] = int(
                MyCash / (HoldNum - len(MyPosition)) / price / 10)  

            MyCash -= MyPosition[code_] * price * 10 

    ratio = round((PosValue - Start_Cash) / Start_Cash * 100,2)
    
    # 今日收益
    if len(daily_netvalue)>0:
        last_trading_date_value = daily_netvalue[-1]
        daily_profit = round((PosValue-last_trading_date_value['当前市值'])/last_trading_date_value['当前市值']*100,2)
    else:
        last_trading_date_value=0
        daily_profit=ratio
        
        
        
    daily_netvalue.append({'日期':today_date,'当前市值':PosValue,'收益率':ratio,
                           '最大回撤':round(Withdraw * 100, 2),'daily_profit':daily_profit})
    
    log.info(today_date + ': 最高市值 ' + str(HighValue) + ' , 当前市值 ' + str(PosValue) + '收益率 ： '
             + str(ratio) + '% , 最大回撤 ' + str(round(Withdraw * 100, 2)) + '%' +' 当日收益' + str(daily_profit) + ' %')
    
    ticker_list = list(MyPosition.keys())
    
    df=data[data['tickerBond'].isin(ticker_list)]
    df=df.reset_index()
    df=df[['tickerBond','closePriceBond','bondPremRatio','secShortNameBond','tickerEqu','remainSize']]
    df['tradeDate']=today_date
    
    holding_list.append(df)

        
    current_day = current_day + 1
    formator()