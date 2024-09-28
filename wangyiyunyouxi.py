# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 网易云游戏
# @Author qianfanguojin
# @Time 2024.09.28
# -------------------------------
# cron "15 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('网易云游戏');

import os
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests

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


class RUN:
    def __init__(self, index, info) -> None:
        self.index = index + 1
        self.authorization = info
        self.s = requests.session()
        self.s.verify=False

    def sign(self):
        url = 'https://n.cg.163.com/api/v2/sign-today'
        header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5',
            'Authorization': self.authorization,
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'n.cg.163.com',
            'Origin': 'https://cg.163.com',
            'Referer': 'https://cg.163.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'X-Platform': '0'
        }
        res = self.s.post(url=url, headers=header).status_code
        if res == 200:
            Log(f"✅ 签到成功")
            return True
        else:
            Log(f"ℹ️ 已经签到了！！")
            return False
    def main(self):
        try:
            Log(f"\n=======\t开始执行第 {self.index}个账号")
            Log(f"\n==>💥 签到")
            self.sign()
            Log(f"\n=======\t第{self.index}个账号执行完毕")
            return True
        except Exception as e:
            Log(f"！！！执行异常: {str(e)}")
            return False

if __name__ == "__main__":
    APP_NAME = '网易云游戏'
    ENV_NAMES = ('WANGYIYUNYOUXI_COOKIES',)
    CK_NAME = 'Authorization值'
    CK_EX = 'Basic ejxxxx'
    CK_URL = 'https://n.cg.163.com'
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
    {APP_NAME}签到
✨ 抓包步骤：
    打开电脑浏览器， F12 打开开发人员工具，选择网络（Network）
    打开{APP_NAME} PC 网页
    找 {CK_URL} 请求头中的Authorization
# 环境变量设置:
✨ 设置青龙变量：
    export {ENV_NAMES[0]}='{CK_NAME}'参数值，多账号#或&分割
✨ 推荐cron：15 8 * * *
✨✨✨ @Author qianfanguojin ✨✨✨
''')
    if not IS_DEV:
        RANDOM_DELAY_RUN()
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.23'
    ENV = {
        "WANGYIYUNYOUXI_COOKIES": "",
    }
    for env_name in ENV_NAMES:
        if not os.getenv(env_name):
            print(f"未填写 {env_name} 变量\n青龙可在环境变量设置 {env_name} 或者在本脚本文件上方往 ENV 字典中填充 {env_name} 对应的值")
            exit()
        ENV[env_name] = os.getenv(env_name)
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
