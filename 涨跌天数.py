import pandas as pd

code ='600519' # 贵州茅台
result_dict={}

# 获取所有日线数据
df = DataAPI.MktEqudGet(secID=u"",ticker=code,tradeDate=u"",
beginDate=u"20050101",endDate=u"20211119",
isOpen="",field=u"",pandas="1")

# 接下来的是统计数据
total_raise = round((df['closePrice'].iloc[-1]/df['closePrice'][0]-1)*100,2) # 区间涨幅
result_dict['total_raise']=total_raise
total_day = len(df)
z_day=len(df[df['chgPct']>=0]) # 涨的天数
d_day=len(df[df['chgPct']<0])  # 跌的天数

# 计算涨跌比例 以防除零出错
if d_day==0:
    d_day=0.0001
day_percent = round((z_day*1.0/d_day)*100,2)

result_dict['day_percent']=day_percent
result_dict['raise_day']=z_day
result_dict['down_day']=d_day
result_dict['days']=total_day # 总共天数


# 重采样，按周，按月，按年算
df['tradeDate']=pd.to_datetime(df['tradeDate'])
new_df = df.set_index('tradeDate')

month_df = new_df.resample('M').sum()
year_df = new_df.resample('A').sum()
week_df = new_df.resample('W').sum()

z_month = len(month_df[month_df['chgPct']>=0])
d_month = len(month_df[month_df['chgPct']<0])
total_month = len(month_df)

if d_month==0:
    d_month=0.0001

month_percent = round((z_month*1.00/d_month)*100,2)

result_dict['month_percent']=month_percent
result_dict['raise_month']=z_month
result_dict['down_month']=d_month
result_dict['months']=total_month # 总共天数
# sub_dict['raise']=total_raise


z_week = len(week_df[week_df['chgPct']>=0])
d_week = len(week_df[week_df['chgPct']<0])
week_len = len(week_df)

if d_week==0:
    d_week=0.0001

week_percent = round((z_week*1.00/d_week)*100,2)
result_dict['week_percent']=week_percent
result_dict['raise_week']=z_week
result_dict['down_week']=d_week
result_dict['weeks']=total_month # 总共天数

z_year= len(year_df[year_df['chgPct']>=0])
d_year = len(year_df[year_df['chgPct']<0])
total_year = len(year_df)

if d_year==0:
    d_year=0.0001

year_percent = round((z_year*1.00/d_year)*100,2)
result_dict['year_percent']=year_percent
result_dict['raise_year']=z_year
result_dict['down_year']=d_year
result_dict['years']=total_year # 总共天数

print(result_dict,'result_dcit')