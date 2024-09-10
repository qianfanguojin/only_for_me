# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# cron "23 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('天翼云盘签到');
import base64
import os
import re
import time
import requests
import rsa
from os import path
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
def LOAD_SEND():
    cur_path = os.path.abspath(path.dirname(__file__))
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

#随机延迟运行
def RANDOM_DELAY_RUN(min_delay=60, max_delay=120):
    import random
    delay = random.uniform(min_delay, max_delay)
    #print(f"随机延迟{delay}秒")
    time.sleep(delay)

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

class RUN:
    def __init__(self,info,index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        self.userid = split_info[0]
        self.pwd = split_info[1]
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            print('检测到设置了UID')
            print(last_info)
            self.send_UID = last_info
        self.index = index + 1

        self.b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        self.UA = 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6'
        self.headers = {
            'User-Agent': self.UA,
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }

    @staticmethod
    def int2char(a):
        return list("0123456789abcdefghijklmnopqrstuvwxyz")[a]

    def b64tohex(self, a):
        d = ""
        e = 0
        c = 0
        for i in range(len(a)):
            if list(a)[i] != "=":
                v = self.b64map.index(list(a)[i])
                if e == 0:
                    e = 1
                    d += self.int2char(v >> 2)
                    c = 3 & v
                elif e == 1:
                    e = 2
                    d += self.int2char(c << 2 | v >> 4)
                    c = 15 & v
                elif e == 2:
                    e = 3
                    d += self.int2char(c)
                    d += self.int2char(v >> 2)
                    c = 3 & v
                else:
                    e = 0
                    d += self.int2char(c << 2 | v >> 4)
                    d += self.int2char(15 & v)
        if e == 1:
            d += self.int2char(c << 2)
        return d

    def rsa_encode(self, j_rsakey, string):
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        return self.b64tohex(
            (base64.b64encode(rsa.encrypt(f"{string}".encode(), pubkey))).decode()
        )

    def login(self):
        # https://m.cloud.189.cn/login2014.jsp?redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html
        url = ""
        urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
        r = s.get(urlToken)
        pattern = r"https?://[^\s'\"]+"  # 匹配以http或https开头的url
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            url = match.group()  # 获取匹配的字符串
            # print(url)  # 打印url
        else:  # 如果没有找到匹配
            print("没有找到url")

        r = s.get(url)
        # print(r.text)
        pattern = r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\""  # 匹配id为j-tab-login-link的a标签，并捕获href引号内的内容
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            href = match.group(1)  # 获取捕获的内容
            r = s.get(href)
            # print("href:" + href)  # 打印href链接
        else:  # 如果没有找到匹配
            print("没有找到href链接")
            exit()

        captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
        paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        s.headers.update({"lt": lt})

        username = self.rsa_encode(j_rsakey, self.userid)
        password = self.rsa_encode(j_rsakey, self.pwd)
        url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
        headers = {
            'User-Agent': self.UA,
            'Referer': 'https://open.e.189.cn/',
        }
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username}",
            "password": f"{{RSA}}{password}",
            "validateCode": "",
            "captchaToken": captchaToken,
            "returnUrl": returnUrl,
            "mailSuffix": "@189.cn",
            "paramId": paramId
        }
        r = s.post(url, data=data, headers=headers, timeout=5)
        if (r.json()['result'] == 0):
            Log('✅ 登陆成功！')
            #print(r.json()['msg'])
        else:
            Log(f"登陆失败！：{r.json()['msg']}")
        redirect_url = r.json()['toUrl']
        r = s.get(redirect_url)
        if r.status_code == 200:
            return r
        else:
            return False

    def signIn(self):
        Log('>>>>>>签到')
        rand = str(round(time.time() * 1000))
        # print(rand)
        surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'

        response = s.get(surl, headers=self.headers)
        netdiskBonus = response.json()['netdiskBonus']
        if (response.json().get('isSign','false') == "false"):
            Log(f"✅ 签到成功，签到获得{netdiskBonus}M空间\n")
        else:
            Log(f"⚠️ 已经签到过了，签到获得{netdiskBonus}M空间\n")

    def lottery(self):
        Log('>>>>>>抽奖')
        url_list = ['https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN',
                    'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN',
                    'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN']
        for index, urls in enumerate(url_list):
            response = s.get(urls, headers=self.headers)
            if ("errorCode" in response.text):
                Log(f"链接{index + 1}抽奖失败")
                print(response.text)
            else:
                description = response.json()['prizeName']
                Log(f"链接{index + 1}抽奖获得{description}\n")

    def main(self):
        Log(f"\n开始执行第{self.index}个账号【{self.userid[-4:]}】--------------->>>>>")
        if not self.login():
            print(f'\n第{self.index}个账号【{self.userid[-4:]}登陆失败！')
            return False
        self.signIn()
        self.lottery()
        return True



if __name__ == '__main__':
    APP_NAME = '天翼云盘'
    ENV_NAME = 'TYYP_COOKIE'
    CK_NAME = '手机号@密码'
    print(f'''
✨✨✨ {APP_NAME}签到抽奖✨✨✨
✨ 功能：
      签到
      抽奖
参数示例：18888888888@123456
✨ 设置青龙变量：
export {ENV_NAME}='{CK_NAME}参数值'多账号#或&分割
✨ 推荐cron：0 9 * * *
✨✨✨ @Author CHERWIN✨✨✨
✨✨✨ @Modify qianfanguojin✨✨✨
''')
    if not IS_DEV:
        RANDOM_DELAY_RUN()
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.10'
    token = ''
    ENV = os.getenv(ENV_NAME)
    token = ENV if ENV else token
    if not token:
        print(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入token =''")
        exit()
    tokens = ENV_SPLIT(token)
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        access_token = []
        for index, infos in enumerate(tokens):
            s = requests.session()
            s.verify=False
            run_result = RUN(infos, index).main()
            if not run_result: continue

    # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()
    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
