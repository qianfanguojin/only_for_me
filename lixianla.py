# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 离线啦论坛
# @Author qianfanguojin
# @Time 2024.09.16
# @Url https://lixianla.com/
# -------------------------------
# cron "56 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('离线啦论坛签到');

# 离线啦论坛为玩家提供最新的STEAM游戏账号,
# steam离线账号,steam联机账号,游戏账号,单机游戏资源,游戏资源等,
# 专注于Steam离线账号共享,steam联机账号分享。

# 电脑登录 https://lixianla.com/ ，打开开发者工具，复制任意请求的 cookie 值
# 环境变量 LXL_COOKIE 设置为复制的 cookie 值
# -------------------------------
APP_NAME = '离线啦 Steam 账号共享论坛'
ENV_NAME = 'LXL_COOKIE'
# ✨✨✨ 离线啦 Steam 账号共享论坛签到✨✨✨
# ✨ 功能：
#     离线啦 Steam 账号共享论坛 签到获取经验、金币，可用于论坛权限帖子访问，账号分享可能需要积分才能查看
# ✨ 变量获取：
#     打开 https://lixianla.com/ , 登录账号，按 F12 打开开发者工具，复制任意请求的 cookie 值
#     关键的 cookie 其实是 bbs_sid 和 bbs_token 两个值就可
# ✨ 变量示例：
#     export LXL_COOKIE='bbs_sid=meohxx; bbs_token=3XDeDhxx'，多账号#或&分割
# ✨✨✨ @Author qianfanguojin ✨✨✨

import os
from bs4 import BeautifulSoup
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import ddddocr

# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)
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
    def __init__(self,cookie, index):
        self.cookie = cookie
        self.index = index + 1
        Log(f"\n==============\t 开始执行第{self.index}个账号 \t==============\n")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
        headers = {
            "User-Agent": user_agent,
            "Cookie": cookie
        }
        self.s = requests.session()
        self.s.verify = False
        self.s.headers.update(headers)
    def parse_captcha(self, image_content):
        # 使用OCR识别验证码
        ocr = ddddocr.DdddOcr(beta=True,show_ad=False)
        #image = open(image_path, "rb").read()
        ocr.set_ranges(5)
        result = ocr.classification(image_content, png_fix=True)
        return result
    # 签到
    def sign_in(self):
        result = self.s.get(url="https://lixianla.com/")
        soup = BeautifulSoup(result.text, "html.parser")
        check_button = soup.select(f'button[data-modal-title="签到"]')
        check_url_path = check_button[0].attrs["data-modal-url"]
        result = self.s.get(f"https://lixianla.com/{check_url_path}")

        soup = BeautifulSoup(result.text, "html.parser")
        vcode_img = soup.select(f'img[title="点击更新"]')
        if len(vcode_img) == 0:
            print("已经签到了！！")
            return
        vcode_url_path = vcode_img[0].attrs["src"]

        response = self.s.get(f"https://lixianla.com/{vcode_url_path}")

        # 解析验证码
        captcha = self.parse_captcha(response.content)

        data = {
            "vcode": captcha
        }
        result = self.s.post(f"https://lixianla.com/{check_url_path}", data=data)
        if result.status_code == 200:
            Log(f"\n\n✅ 签到成功！！")

        #print(result.text)
    def get_personal_info(self, end=False):
        result = self.s.get("https://lixianla.com/my-credits.htm")
        soup = BeautifulSoup(result.text, "html.parser")
        self.user_name = soup.find("span", class_='h4 font-weight-bold').text.strip()
        Log(f"用户名：{self.user_name}")
        info_divs = soup.find_all("div", class_='input-group mb-3')
        for info in info_divs:
            label = info.find("span", class_='input-group-text').text.strip()
            value = info.find("input", type='text')['value']
            Log(f"{label}：{value}")
        #去除引号
        return self.user_name
    def main(self):
        try:
            # 获取执行前用户信息
            Log(f"\n==>🧑 读取用户信息")
            self.get_personal_info()
            # 签到
            Log(f"\n==>💥 签到")
            self.sign_in()
            # 获取执行后用户信息
            Log(f"\n==>🧑 读取用户信息")
            self.get_personal_info()
            Log(f"\n==============\t 第{self.index}个账号执行完毕 \t==============\n")
        except Exception as e:
            Change_status("出错")
            Log(f"！！！执行异常: {str(e)}")
            return False
if __name__ == '__main__':
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.15'
    token = ''
    ENV = os.getenv('LXL_COOKIE')
    token = ENV if ENV else token
    if not token:
        Log(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将环境变量填入token =''")
        exit()
    tokens = ENV_SPLIT(token)
    if len(tokens) > 0:
        Log(f"\n==============\t 共获取到{len(tokens)}个账号 \t============== ")
        for index, infos in enumerate(tokens):
            if not infos or infos == '':
                Log(f"{ENV_NAME}变量填写格式错误，请检查")
            run_result = RUN(infos, index).main()
            if not run_result: continue
    # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()

    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
