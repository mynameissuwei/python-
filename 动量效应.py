from jqdatasdk import *
import datetime

auth('18817582839', 'Suwei1996728')

last_150_days = datetime.date.today() - datetime.timedelta(days=150)

today = datetime.datetime.today().strftime("%Y-%m-%d")
all_securities_pd = get_all_securities()
filtered_securities_pd = all_securities_pd[all_securities_pd.end_date>today]
# filtered_securities_pd = filtered_securities_pd[filtered_securities_pd.start_date<last_150_days]

print(filtered_securities_pd)

if __name__ == '__main__':
    print('it works')