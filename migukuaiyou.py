# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 咪咕快游
# @Author qianfanguojin
# @Time 2024.09.28
# -------------------------------
# cron "7 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('咪咕快游');
# -------------------------------
APP_NAME = '咪咕快游'
ENV_NAMES = ('MIGUKUAIYOU_COOKIES',)
# ✨✨✨ 咪咕快游签到✨✨✨
# ✨ 功能：
#     咪咕快游签到
# ✨ 抓包步骤：
#     1.    打开电脑浏览器，打开咪咕快游PC 网页
#           F12 打开开发人员工具，选择应用程序，本地存储，点击 {CK_URL} 项
#           找到 cryptoSign cryptoUserId cryptoUserToken 三项对应的值
#     2.    打开咪咕快游手机 APP，打开抓包软件，进入 我的>电玩体验馆>签到
#           观看一条广告视频，在 https://betagame.migufun.com/member/newSign/v1.0.7.7/reportLookAds 请求头中
#           找到 mgHeaders 值
#     最后组装为: cryptoSign值@cryptoUserId值@cryptoUserToken值@mgHeaders值
# ✨ 变量示例：
#     export MIGUKUAIYOU_COOKIES='fed9xx@04fad981845xx@0467b88ec5dxx@7JZxSVYdvPxxx'，多账号#或&分割
# ✨✨✨ @Author qianfanguojin ✨✨✨

import os
import random
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
        self.app_ad_mgheaders = split_info[3]

    def get_user_info(self):
        url = 'http://betagame.migufun.com/member/memberights/v1.0.1.5/queryMemberRightsAndTime'
        header = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "headerSign": self.header_sign,
            "userId": self.user_id,
            "userToken": self.user_token,
            "hgv": "5rPulhA0y"
        }
        msgheaders = Crypt.encrypt_data(json.dumps(header,separators=(',', ':')))
        header.update({"mgheaders": msgheaders})
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
                Log(f"ℹ️  今日已签到，{query_month} 已连续签到 {sign_days} 天")
                return True
            Log(f"✅ 签到成功, {query_month} 已连续签到 {sign_days} 天")
            return True
        else:
            Change_status("异常")
            return False

    def watch_video(self):
        url = "http://betagame.migufun.com/member/newSign/v1.0.7.7/reportLookAds"
        payload = "tE0gx3d9Iud/Svs4RmXivQ=="
        headers = {
            'User-Agent': "okhttp/3.9.1",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'mgHeaders': self.app_ad_mgheaders,
            'Content-Type': "application/json; charset=utf-8"
        }
        #由于无法解析观看结果，默认是四条广告视频，所以循环四次，多次观看不叠加
        for i in range(1, 5):
            time.sleep(random.randint(1, 3))
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                Log(f"✅ 观看广告视频 {i} 成功")
                continue
            else:
                Log(f"❌ 观看视频 {i+1} 失败")

    def main(self):
        try:
            Log(f"\n=======\t开始执行第 {self.index} 个账号")
            Log(f"\n==>🆕 变量准备")
            self.init_var()
            Log(f"\n==>🧑 读取用户信息")
            self.get_user_info()
            Log(f"\n==>💥 签到")
            self.sign()
            Log(f"\n==>📺️ 看广告视频")
            self.watch_video()
            Log(f"\n==>🧑 读取用户信息")
            self.get_user_info()
            Log(f"\n=======\t第 {self.index} 个账号执行完毕")
            return True
        except Exception as e:
            Log(f"！！！执行异常: {str(e)}")
            return False

if __name__ == "__main__":


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
