# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 夸克网盘
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2024/5/4 16:23
# @Modify : qianfanguojin✨✨✨ https://github.com/qianfanguojin/only_for_me
# @Time : 2024/9/8 16:23
# -------------------------------
# cron "0 0 2 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('夸克签到')

import requests
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)
if os.path.isfile('.env'):
    IS_DEV = True
    from dotenv import load_dotenv
    load_dotenv('.env')
else:
    IS_DEV = False

class RUN:
    def __init__(self, info, index):
        self.cookie = info
        self.index = index + 1

    def init_var(self):
        import http
        c = http.cookies.SimpleCookie()
        c.load(self.cookie)
        self.cookie_dict = {}
        for key, morsel in c.items():
            self.cookie_dict[key] = morsel.value
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            "content-type": "application/json",
            "cookie": self.cookie,
        }
        self.s.headers.update(self.headers)
        self.base_url = "https://pan.quark.cn"

    def request_json(self, method, url, params=None, data=None, json=None):
        """
        发起请求获取json响应

        Args:
            url (_type_): 请求url
            cookie (_type_, optional): 请求的cookie. Defaults to None.
            params (_type_, optional): 请求的参数. Defaults to None.

        Returns:
            _type_: json响应
        """

        try:
            response = self.s.request(method, url, headers=self.headers, params=params, data=data, json=json)
            response.raise_for_status()  # 如果响应状态码不是 200-299，会引发 HTTPError
            return {'status': 'success', 'data': response.json()}
        except requests.RequestException as e:
            return {'status': 'error', 'error': str(e), 'response': response.text if response else 'No response'}


    def get_account_info(self):
        # 创建 3 个 issue
        url = f"{self.base_url}/account/info"
        querystring = {"fr": "pc", "platform": "pc"}
        response = self.request_json("GET", url, params=querystring)
        if response.get("data",'').get("data",''):
            self.account_info = response["data"]["data"]
            Log(f" 昵称: {self.account_info['nickname']}")
            return True
        else:
            Log("\n❌该账号登录失败，cookie无效")
            return False

    def get_growth_info(self):
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {
            "kps": "AAS690MXOIgd7fQnWtDvqbp10M7jfsNAmTappgrG3//2djuZQr1caugCLvALZ0a6/oTSAzqZ/cp+iUAkpjzXJcTOuUwzo4XqxunDQcj92KiufE/CZdU8a9Xw+vYsmm3yT+A%3D",
            "sign": "AATKvg134BGOAn79kIf1N1tp8cDypYCctRkAcPcWrM2lBlwsoyH9SWrzlQQUHGCzEH8%3D",
            "vcode": "1725815096337",
            "pr": "ucpro",
            "fr": "android",
        }
        response = self.request_json("GET", url, params=querystring)
        if response.get("data",'').get("data",''):
            return response["data"]["data"]
        else:
            return False
    def get_growth_sign(self):
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {
            "kps": "AAS690MXOIgd7fQnWtDvqbp10M7jfsNAmTappgrG3//2djuZQr1caugCLvALZ0a6/oTSAzqZ/cp+iUAkpjzXJcTOuUwzo4XqxunDQcj92KiufE/CZdU8a9Xw+vYsmm3yT+A%3D",
            "sign": "AATKvg134BGOAn79kIf1N1tp8cDypYCctRkAcPcWrM2lBlwsoyH9SWrzlQQUHGCzEH8%3D",
            "vcode": "1725815096337",
            "pr": "ucpro",
            "fr": "android",
        }
        payload = {"sign_cyclic": True}
        response = self.request_json("POST", url, json=payload, params=querystring)
        if response.get("data",'').get("data"):
            return True, response["data"]["data"]["sign_daily_reward"]
        else:
            return False, response["message"]

    def main(self):
        try:
            # 初始化变量
            self.init_var()
            msg = ""
            # 验证账号
            self.get_account_info()
            Log(f"\n---------开始执行第{self.index}个账号>>>>>")
            # 每日领空间
            growth_info = self.get_growth_info()
            if growth_info:
                if growth_info["cap_sign"]["sign_daily"]:
                    log = f"✅ 执行签到: 今日已签到+{int(growth_info['cap_sign']['sign_daily_reward'] / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})"
                    msg += log + "\n"
                    Log(msg)
                else:
                    sign, sign_return = self.get_growth_sign()
                    if sign:
                        log = f"✅ 执行签到: 今日签到+{int(sign_return / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})"
                        msg += log + "\n"
                        Log(msg)
                    else:
                        msg += f"✅ 执行签到: {sign_return}\n"
                        Log(msg)
        except Exception as e:
            Change_status("出错")
            Log(f"！！！执行异常: {str(e)}")
            return False
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
        # print(parts)
        return (parts)

    elif '#' in input_str:
        hash_parts = input_str.split('#')
        # print(hash_parts)
        return (hash_parts)
    else:
        out_str = str(input_str)
        # print([out_str])
        return ([out_str])

send_msg = ''
one_msg=''
SCRIPT_STATUS="正常"

def Change_status(status, msg=''):
    global SCRIPT_STATUS
    if msg:
        SCRIPT_STATUS = status + f"-{msg}"
    SCRIPT_STATUS = status
def Log(cont=''):
    global send_msg,one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'



if __name__ == '__main__':
    APP_NAME = '夸克网盘'
    ENV_NAME = 'QUARK_COOKIE'
    CK_NAME = 'cookie'
    CK_URL = 'https://pan.quark.cn/'
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
    {APP_NAME}签到，签到可获得容量
✨ 设置青龙变量：
    export {ENV_NAME}='{CK_NAME}'参数值，多账号#或&分割
    示例：export {ENV_NAME}='cookie1&cookie2'
✨ 推荐cron：55 9 * * *
✨✨✨ @Author qianfanguojin ✨✨✨
''')
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.08'
    token = ''
    ENV = os.getenv(ENV_NAME)
    token = ENV if ENV else token
    if not token:
        Log(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入token =''")
        exit()
    tokens = ENV_SPLIT(token)
    if len(tokens) > 0:
        Log(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        for index, infos in enumerate(tokens):
            if not infos or infos == '':
                Log(f"{ENV_NAME}变量填写格式错误，请检查")
            run_result = RUN(infos, index).main()
            if not run_result: continue
    import notify
    if notify.send: notify.send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)




