# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author qianfanguojin✨✨✨ @2024.09.01
# -------------------------------

import os
import requests
import urllib3
import time
from urllib3.exceptions import InsecureRequestWarning
# import CHERWIN_TOOLS
# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)
IS_DEV = False
if os.path.isfile('.env'):
    IS_DEV = True
    from dotenv import load_dotenv
    load_dotenv('.env')
else:
    IS_DEV = False

def get_saas_token(login_credentials):
    headers = {
        "Host": "newapi.gijsq.com",
        "User-Agent": "PC/Windows/windows10.0.26100.1591x64/2/GIAcceler-PC/1.4.6/40EC99834285",
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
        "Login-Credential": login_credentials,
        "Saas-App-Id": "GI_PC",
        "Saas-Product-Line": "GI",
    }
    s = requests.session()
    s.verify = False
    s.headers.update(headers)
    url = f"https://newapi.gijsq.com/api/common_bll/v1/member/login_status?client_type=10&version=1.4.6"
    result = s.get(url,params=None)
    token = result.headers.get("Set-Saas-Token")
    return token
def checking(login_credentials):
    headers = {
        "Refer": "https://servicewechat.com/wx820ac60d61fc054e/6/page-frame.html",
        "Host": "newwin.gijsq.com",
        "useragent": "browser/system_type/system_version/1332/giacceler-applet/1.0.0/terminal_code",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; 23013RK75C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/8758 MicroMessenger/8.0.50.2701(0x2800323E) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
        "Login-Credential": login_credentials,
        "Saas-App-Id": "GI_PC",
        "Saas-Product-Line": "GI",
    }
    s = requests.session()
    s.verify = False
    s.headers.update(headers)
    #每日签到
    url = "https://newapi.gijsq.com/api/common_bll/v1/activity/free/task/award?client_type=10&product_line=gi&task_type=free&version=1.4.6"
    result = s.get(url,headers=headers)
    print(result.text.encode('utf-8').decode('unicode_escape'))
    for i in range(5):
        #每日看广告
        url = "https://newwin.gijsq.com/api/common_bll/v1/activity/free/task/award?product_line=gi&task_type=watch_adv"
        result = s.get(url,headers=headers)
        time.sleep(30)
        print(result.text.encode('utf-8').decode('unicode_escape'))

login_credentials = os.getenv('GI_LOGIN_CREDENTIALS')
APP_NAME = 'Gi加速器'
ENV_NAME = 'GI_LOGIN_CREDENTIALS'
CK_NAME = 'Login-Credential'
CK_URL = 'https://newapi.gijsq.com/api/common_bll/v1/member/login_status'
print(f'''
✨✨✨ {APP_NAME}签到领取时长✨✨✨
✨ 抓包步骤：
    打开Windows抓包工具
    打开{APP_NAME}
    登录，已登录则点击获取时长页面
    找{CK_URL}的URl(如果已经授权登陆先退出登陆)
    复制里面的{CK_NAME}参数值
    参数示例：2024090718xxxx_xxxx"
✨ 功能：
    {APP_NAME}签到领取时长，时长可用于游戏加速
✨ 设置青龙变量：
    export {ENV_NAME}='{CK_NAME}'参数值，
✨ 推荐cron：30 11 * * *
✨✨✨ @Author qianfanguojin ✨✨✨
''')
checking(login_credentials)
