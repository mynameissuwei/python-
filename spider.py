import os
import time
import datetime
import random
import pandas as pd
import urllib.request as request
import json
import numpy as np


def get_content_from_internet(url):
    """
    从指定的url获取数据
    :param url:
    :return: str:页面内容
    """
    max_try = 10
    timeout = 15
    wait_time = 10
    flag = False
    print(range(max_try))
    for i in range(max_try):
        try:
            content = request.urlopen('http://hq.sinajs.cn/rn=34101&list=sh000001', timeout=timeout).read()
            flag = True
            break
        except Exception as e:
            print("获取数据失败第", i + 1, "次，报错内容：", e)
            time.sleep(wait_time)
    if flag:
        return content
    else:
        raise ValueError("获取数据url不停报错，停止运行!")


if __name__ == '__main__':
    get_content_from_internet('http://www.baidu.com')