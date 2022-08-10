import json
import requests
import pandas as pd


def send_message(_message):
    useridstr = 'SuWei'
    agentid = '1000002'
    corpid = 'ww0c853682753f25c2'
    corpsecret = 'kH5V-GvJfaQ7r-V6HyDKEfld0ny-OfoTyRoVy7jF5rk'
    response = requests.get(f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}")
    data = json.loads(response.text)
    access_token = data['access_token']
    json_dict = {
       "touser" : useridstr,
       "msgtype" : "text",
       "agentid" : agentid,
       "text" : {
           "content" : _message
       },
       "safe": 0,
       "enable_id_trans": 1,
       "enable_duplicate_check": 0,
       "duplicate_check_interval": 1800
    }
    json_str = json.dumps(json_dict)
    response_send = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    print(response_send.text,'json_str')
    return json.loads(response_send.text)['errmsg'] == 'ok'

for _ in range(1):
	send_message("中概互联涨停啦")