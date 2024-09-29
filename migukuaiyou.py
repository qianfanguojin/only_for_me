# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 咪咕快游
# @Author qianfanguojin
# @Time 2024.09.28
# -------------------------------
# cron "7 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('咪咕快游');

import os
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad,unpad
import base64
import json

# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)
if os.path.isfile('.env'):
    IS_DEV = True
    from dotenv import load_dotenv
    load_dotenv('.env')
else:
    IS_DEV = False
def LOAD_SEND():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    notify_file = cur_path + "/notify.py"
    if os.path.exists(notify_file):
        try:
            from notify import send  # 导入模块的send为notify_send
            print("加载通知服务成功！")
            return send  # 返回导入的函数
        except ImportError:
            print("加载通知服务失败~")
    else:
        print("加载通知服务失败~")
    return False  # 返回False表示未成功加载通知服务

# 取环境变量，并分割
def ENV_SPLIT(input_str):
    parts = []
    if '&' in input_str:
        amp_parts = input_str.split('&')
        for part in amp_parts:
            if '#' in part:
                hash_parts = part.split('#')
                for hash_part in hash_parts:
                    parts.append(hash_part)
            else:
                parts.append(part)
        return (parts)

    elif '#' in input_str:
        hash_parts = input_str.split('#')
        return (hash_parts)
    else:
        out_str = str(input_str)
        return ([out_str])

def RANDOM_DELAY_RUN(min_delay=60, max_delay=120):
    import random
    delay = random.uniform(min_delay, max_delay)
    Log(f"\n随机延迟{delay}秒\n")
    time.sleep(delay)

one_msg=''
SCRIPT_STATUS="正常"
def Change_status(status, msg=''):
    global SCRIPT_STATUS
    if msg:
        SCRIPT_STATUS = status + f"-{msg}"
    SCRIPT_STATUS = status
send_msg = ''
def Log(cont=''):
    global send_msg,one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

class Crypt:
    bask = "KV4lJCt3"
    bbsk = "X3gyKiZ+Q"
    bcsk = "CEjKA=="
    basi = "IyZAYV94K3"
    bbsi = "IoJSpefi"
    bcsi = "EpJA=="
    def decode(value):
        # 此函数需要实现与 v.a.decode 相同的功能
        return base64.b64decode(value).decode('utf-8')
    def encrypt_data(data):
        key = Crypt.decode(Crypt.bask + Crypt.bbsk + Crypt.bcsk)
        iv = Crypt.decode(Crypt.basi + Crypt.bbsi + Crypt.bcsi)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_data(encrypted_data):
        key = Crypt.decode(Crypt.bask + Crypt.bbsk + Crypt.bcsk)
        iv = Crypt.decode(Crypt.basi + Crypt.bbsi + Crypt.bcsi)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted.decode('utf-8')


class RUN:

    def __init__(self, index, info) -> None:
        self.index = index + 1
        self.info = info
        self.s = requests.session()
        # self.s.mount('https://', TLSAdapter())
        self.s.verify=False


    def init_var(self):
        split_info = self.info.split("@")
        self.header_sign = split_info[0]
        self.user_id = split_info[1]
        self.user_token = split_info[2]

    def get_user_info(self):
        url = 'http://betagame.migufun.com/member/memberights/v1.0.1.5/queryMemberRightsAndTime'
        header = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "headerSign": self.header_sign,
            "userId": self.user_id,
            "userToken": self.user_token,
            "hgv": "5rPulhA0y",
            "mgheaders": "FaDuFvJY3837NmqhLnp9+Uqqp3pFxW8/t1rCtoe1Lov90UuulRvWEeKnx+/aQjiFR7K2JiF3uNgUnhQgjK0Eh1hvYiUR+htf+u2gTj+3HnWwQWZU7ujIg9wDCDBXv/sFqvOpCrPlMOgtsruvd7aVkYT3T6+j4kWOaxuZcsxGo3M6n2mGY8Rd1NpNyNM4zEkd4ohIzsnZY4LPTqDyTW2aDLTlmX9cQbH9XExvDG+wdxFVf4VHNM/89PbEFI4PmJ/cqi8uV4EZ4kG/GnChzKa4q2oHT7S8k+yWIaw2oq3ro9O8LWHcdtbfOzR6hSN8RCkRtXd+IUh+Q6k6ka5qAJItiwZofzJfJURcGqcxd5fQYbSPZjb+o9PteWfk5V1A7oFP6JZoj46RyZd2WY5iEiw0mmPMeYqz8aXGmp08cFlROqhBEwYqeSHWDK5FU0whIajvgPuKpMT4ZU/4coRHxen9wOnT5Rp9aeUbZmhpT/BsAEcwzN4fwAtRV+AVMz6bDmM2b78n/qhtQlk/Vlxd7TEwxPmeyOTICqf4kAjAmi1+gsHM4ZLIu4WYHUwGTvKl1wWOD/Xfg7SQ7AeCi4mpGfWKp/EXtzSVu3AbhbgyqaWJaCntwIn/VRzg7iazvO/+5RPB/uAEtjnVb1iZaVLlfuyHCZCPPrSvOS2b94dHPD0IuYpschTSZZOL0V4v2otmaZ9GelzacvGLSm5VCKFHSuTvURYw4/U1/jKDkq7mXLxa4t+QYoZx6SplMJSMZ+xN7yDW/61SDHLKO+KIeyNGMp4zdTSUvmEYuev72yjROB/WjpfVBBLibCcv51mGWgpJRTSuCxAc4Q1Q7ir1NTwpPtnv7UDfs87c8QLvskRiNRDOE7PFEGIhxB5tigaq4WITlLSHGmwnyaVg4jJrgbISa8/PPd5d04A+6WO24X5424AgMQKPL+uzJF4SMCHImAumVYY/f9ziT4yvYsqN2QfqB+GCSTz64x2Ct2idxTXwSCZS1mNRFZOgxzOXfeF/RLwYZxnWaIxZ/oqNitdNBBz91g72sFggYYJvRM3JoNRWgS/570gT6lzM4fqUaTyQsIe3ziy1FYnES2kuXtNh9ioRGmTp/+taNNJdGSvq3n2NJ3P53R9tEVLrrJXAo3H2Gact3YvdF6HIi4L0gZwfXYqhzglKTdpF0MbZrjWUJw8PFpUG4HAL3sDQ6vFqWi2+2UnVYNpg7hj0T6bJMUG9dqC8MZxSmUFjrmJdxlGwThqVJRcOjBS42MF7OdODzX+XcoA5Sd/9yU3O83h4JxTFS8hmcYpndlF1ZRdty8V4exqzCirCZXtqg21rEe2IMmCa6XSVfP2lNIXS76v7XDfbIlOD7G4Wf0ZooZktRBlqKYWgSRHwb+5/++NPOMZPktdb+agr+Zkf/PE2GZ2z++m2ZthhtadmvmVfVi3XEB/0za8078jxR+3MqPQ2bTq98ZHO5mBk+dWqrFk/sHooRQsa4JB1QlLiDQ=="
        }
        # msgheaders = Crypt.encrypt_data(json.dumps(header))
        # header.update({"msgheaders": msgheaders})
        data = '{"needPop":0,"gameId": null}'
        res = self.s.post(url=url, headers=header, data=Crypt.encrypt_data(data))
        res_json = json.loads(Crypt.decrypt_data(res.text))
        if res.status_code == 200:
            remain_minutes = res_json['resultData']['remainTotalTime'] / 60000
            if remain_minutes:
                Log(f"⌛️ 目前剩余时长 {remain_minutes} 分钟")
            else:
                Log(f"⌛️❌ 剩余时长未知")
        else:
            Change_status("异常")
            return False
    def sign(self):
        url = 'http://betagame.migufun.com/member/newSign/v1.0.6.5/querySignDetails'
        header = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "headerSign": self.header_sign,
            "userId": self.user_id,
            "userToken": self.user_token
        }
        data = {"querySignMonth": 0}
        res = self.s.post(url=url, headers=header, json=data)
        res_json = res.json()
        if res.status_code == 200:
            sign_days = res_json['resultData']['totalSignDays']
            query_month = res_json['resultData']['queryMonth']
            if res_json['resultData']['popResp']['popFlag'] == 0:
                Log(f"ℹ️ 今日已签到，{query_month} 已连续签到 {sign_days} 天")
                return True
            Log(f"✅ 签到成功, {query_month} 已连续签到 {sign_days} 天")
            return True
        else:
            Change_status("异常")
            return False
    def main(self):
        try:
            Log(f"\n=======\t开始执行第 {self.index} 个账号")
            Log(f"\n==>🆕 变量准备")
            self.init_var()
            Log(f"\n==>🧑 读取用户信息")
            self.get_user_info()
            Log(f"\n==>💥 签到")
            self.sign()
            Log(f"\n==>🧑 读取用户信息")
            self.get_user_info()
            Log(f"\n=======\t第 {self.index} 个账号执行完毕")
            return True
        except Exception as e:
            Log(f"！！！执行异常: {str(e)}")
            return False

if __name__ == "__main__":
    APP_NAME = '咪咕快游'
    ENV_NAMES = ('MIGUKUAIYOU_COOKIES',)
    CK_NAME = 'cryptoSign值@cryptoUserId值@cryptoUserToken值'
    CK_EX = 'fed9xx@04fad981845xx@0467b88ec5dxx'
    CK_URL = 'https://www.migufun.com/'
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
    {APP_NAME}签到
✨ 抓包步骤：
    打开电脑浏览器，打开{APP_NAME} PC 网页
    F12 打开开发人员工具，选择应用程序，本地存储，点击 {CK_URL} 项
    找到 cryptoSign cryptoUserId cryptoUserToken 三项对应的值
    组装为: {CK_EX}
✨ 设置青龙变量：
    export {ENV_NAMES[0]}='{CK_NAME}'参数值，多账号#或&分割
✨ 示例：
    export {ENV_NAMES[0]}='{CK_EX}'
✨ 推荐cron：9 8 * * *
✨✨✨ @Author qianfanguojin ✨✨✨
''')
    if not IS_DEV:
        RANDOM_DELAY_RUN()
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.29'
    ENV = {
        ENV_NAMES[0]: "",
    }
    for env_name in ENV_NAMES:
        if os.getenv(env_name):
            ENV[env_name] = os.getenv(env_name)
        elif ENV[env_name]:
            continue
        else:
            print(f"未填写 {env_name} 变量\n青龙可在环境变量设置 {env_name} 或者在本脚本文件上方往 ENV 字典中填充 {env_name} 对应的值")
            exit()
    tokens = ENV_SPLIT(ENV[ENV_NAMES[0]])
    SCRIPT_STATUS = "正常"
    if len(tokens) > 0:
        Log(f"\n=======\t共获取到 {len(tokens)} 个账号")
        for index, info in enumerate(tokens):
            obj = RUN(index, info)
            run_result = obj.main()
            if not run_result:
                SCRIPT_STATUS = "异常"

    # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()

    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
