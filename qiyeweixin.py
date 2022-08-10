#-*- encoding:utf-8 -*-
import requests
import json
from requests_toolbelt import MultipartEncoder

class qywx:
    # 向应用发送文字消息接口，_message为字符串
    def send_text(self, _message, useridlist = ['name1|name2']): 
        useridstr = 'SuWei'
        agentid = '1000002'
        corpid = 'ww0c853682753f25c2'
        corpsecret = 'kH5V-GvJfaQ7r-V6HyDKEfld0ny-OfoTyRoVy7jF5rk'
        response = requests.get(f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}")
        data = json.loads(response.text)
        print(data,'data')

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
        response_send = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(access_token=access_token), data=json_str)
        print(response_send,'response_send')
        return json.loads(response_send.text)['errmsg'] == 'ok'
# 调用示例
if __name__ == '__main__':
    qy = qywx()
    
    # 发送文本消息
    qy.send_text('hello world', ['SuWei'])
    
    # # 发送图片消息, 需先上传至临时素材
    # media_id = qy.post_file('/root/', 'a.jpg')
    # qy.send_img(media_id, ['ZhangSan'])