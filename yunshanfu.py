# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 云闪付签到
# @Author qianfanguojin
# @Time 2024.10.21
# @Description
# ✨ 功能：
#       云闪付签到, 获取积分
# ✨ 抓包步骤：
#       抓包云闪付 APP
#       导航栏 我的 进入签到页面，搜索域名 https://youhui.95516.com/ 获取请求头中的 Authorization 和 Cookie（CookieA）
#       导航栏 优惠 -> 玩赚云闪付 -> 天天赚积分 , 搜索域名 https://yxq.95516.com/，获取请求头中的 Cookie（CookieB）
#       因为是不同平台是不同的请求头，必需要提供抓包的平台代号，如果是安卓为 A，IOS 为 I
#       组装为: 平台&Authorization值&CookieA值&CookieB值
# ✨ 变量示例：
#     export YSF_CREDENTIALS='A&ejxxx&...__tokenat=12321321; _tracker_distinct_id_=123231; canvasId=xzxx%20Object%5D...&...__tokenat=12321321; _tracker_distinct_id_=123231; canvasId=xzxx%20Object%5D...'，多账号换行分割
# -------------------------------
# cron "59 12 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('云闪付签到');
# -------------------------------
import traceback
import requests
from script_tools import BaseRun
import os
import json
import time
import random
import hashlib
import string

class YSFCrypt:
    salt = "duiba123123"
    def get_sign_data(data=None, salt=None, random_str=None, timestamp=None):
        """
        计算连接字符串的 MD5 哈希值

        参数:
        salt (str): 第一个字符串
        random_str (str): 第二个字符串
        timestamp (str): 第三个字符串

        返回:
        str: 计算得到的 MD5 哈希值的十六进制表示
        """
        salt = salt if salt else YSFCrypt.salt
        random_str = random_str if random_str else YSFCrypt.random_str()
        timestamp = timestamp if timestamp else int(time.time() * 1000)
        if data:
            # 如果 data 存在，将其 JSON 序列化后与 salt, random_str, timestamp, 拼接，计算 MD5 哈希
            data_str = json.dumps(data, separators=(',', ':'))  # JSON序列化，去掉多余空白
            combined_str = f"{salt}{data_str}{random_str}{timestamp}"
            sign = hashlib.md5(combined_str.encode()).hexdigest()

            # 更新 s.data 的内容，包含签名、时间戳和随机字符串
            return {
                "data": data_str,
                "timestamp": timestamp,
                "nonceStr": random_str,
                "sign": sign
            }
        elif not data:
            # 如果 data 不存在，拼接 salt, random_str, timestamp 生成签名
            combined_str = f"{salt}{random_str}{timestamp}"
            sign = hashlib.md5(combined_str.encode()).hexdigest()
            # 更新 s.data 为包含签名、时间戳和随机字符串
            return {
                "timestamp": timestamp,
                "nonceStr": random_str,
                "sign": sign
            }
    def random_str(s=16):
        """
        生成一个随机字符串

        参数:
        s (int): 生成的随机字符串长度，默认为16

        返回:
        str: 生成的随机字符串
        """
        # 定义可用字符，包括大写字母、小写字母和数字
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        # 生成随机字符串
        result = ''.join(random.choice(characters) for _ in range(s))
        return result
class Run(BaseRun):

    def init_vars(self):
        self.session = requests.Session()
        self.android_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 23013RK75C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/129.0.6668.100 Mobile Safari/537.36(com.unionpay.mobilepay) (cordova 7.0.0) (updebug 0) (clientVersion 315) (version 1015)(UnionPay/1.0 CloudPay)(language zh_CN)(languageFamily zh_CN)(upHtml)(walletMode 00)",
            "Accept": "application/json, text/plain, */*",
        }
        self.ios_headers = {
            "Host": "youhui.95516.com",
            "Accept": "application/json, text/plain, /",
            #"Authorization": process.env.YSF_TOKEN,
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "x-city": "360900",
            "Sec-Fetch-Mode": "cors",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://youhui.95516.com",
            "Content-Length": "2",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/sa-sdk-ios (com.unionpay.chsp) (cordova 4.5.4) (updebug 0) (version 938) (UnionPay/1.0 CloudPay) (clientVersion 198) (language zh_CN) (upHtml) (walletMode 00)",
            "Referer": "https://youhui.95516.com/newsign/public/app/index.html",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Sec-Fetch-Dest": "empty",
            #"Cookie": process.env.YSF_COOKIE
        }
        #签到，积点获取
        self.base_url = "https://youhui.95516.com/"
    def process_var(self, info):
        platform, token, cookie_youhui, self.cookie_yxq = info.split("&")
        if platform == "I":
            self.headers = self.ios_headers
        else:
            self.headers = self.android_headers
        self.session.headers.update(self.headers)
        self.session.headers['Authorization'] = f"Bearer {token}"
        self.session.headers['Cookie'] = cookie_youhui

    def sign(self):
        result = self.session.post(f'{self.base_url}/newsign/api/daily_sign_in')
        data = result.json()
        if result.status_code != 200:
            self.logger.error(f"❌ 签到失败，原因：{result.text}")
            return False
        if not data.get("repeated") and data.get("signedIn"):
            self.logger.info(f'✅ 签到成功, 目前连续签到天数为{data["signInDays"]["days"]}, 这个月连续签到天数：{data["signInDays"]["current"]["days"]}')
        else:
            self.logger.info(f'ℹ️  已经签到过了, 目前连续签到天数：{data["signInDays"]["days"]}, 这个月连续签到天数：{data["signInDays"]["current"]["days"]}')
        return True

    #玩 “赚” 云闪付，联合签到专区，每个任务 6 积点
    def click_sign_tasks(self):
        session = requests.session()
        headers = {
            'Content-Type': "application/json",
            'Cookie': self.cookie_yxq
        }
        session.headers = headers
        yxq_baseurl = "https://yxq.95516.com/"
        #获取任务列表
        self.logger.debug("获取任务列表")
        url = f"{yxq_baseurl}/taskCenter/api/app/sign/index"
        res_data = session.post(url, data=json.dumps(YSFCrypt.get_sign_data())).json()
        todo_tasks = [task for task in res_data["data"] if not (lambda task: task["taskId"] == 19 or task['taskStatus'] == 2)(task)]
        self.logger.debug(f"共 {len(todo_tasks)} 个任务")
        reward_count = 0
        reward_sum = 0
        for task in todo_tasks:
            time.sleep(random.randint(1, 3))
            try:
                #做任务
                self.logger.info(f"做任务：{task['taskTitle']}")
                url = f"{yxq_baseurl}/taskCenter/api/app/sign/doCompleted"
                sign_data = YSFCrypt.get_sign_data({"taskId": task["taskId"]})
                payload = json.dumps(sign_data)
                res_data = session.post(url, data=payload).json()
                if res_data.get("ok"):
                    self.logger.debug(f"任务完成：{task['taskTitle']}")
                else:
                    self.logger.debug(f"{res_data['msg']}")
                #领奖励
                url = f"{yxq_baseurl}/taskCenter/api/app/task/sendPrize"
                res_data = session.post(url, data=payload).json()
                if res_data.get("ok"):
                    self.logger.debug(f"奖励成功：{res_data['data']['prizeName']}")
                    reward_count += 1
                    reward_sum += res_data['data']['pointPrizeInfo']['pointAt']
                else:
                    self.logger.debug(f"{res_data['msg']}")
            except Exception as e:
                self.logger.error(f"做 {task['taskTitle']} 任务失败：{e}")
            finally:
                continue
        self.logger.info(f"\n🎉 共领 {reward_count} 个任务奖励，合计获得 {reward_sum} 积点")
    def get_personal_info(self):
        result = self.session.get(f'{self.base_url}/newsign/api/users/coins')
        data = result.json()
        if result.status_code != 200:
            self.logger.error(f"❌ 获取积点信息失败，原因：{result.text}")
            return False
        self.logger.info(f'🏅 当前剩余积点：{data["coins"]}')
        return True
    def process(self):
        self.logger.info(f"当前版本：{local_version}")
        if self.app_env_infos:
            self.logger.info(f"\n=======\t共获取到 {len(self.app_env_infos)} 个账号")
        else:
            return
        for index, info in enumerate(self.app_env_infos):
            try:
                self.logger.info(f"\n=======\t开始执行第 {index + 1} 个账号")
                self.process_var(info)
                self.logger.info(f"\n==> 去签到")
                self.sign()
                self.logger.info(f"\n==> 玩 “赚” 云闪付，联合签到专区")
                self.click_sign_tasks()
                self.logger.info(f"\n==> 获取用户信息")
                self.get_personal_info()
                return True
            except Exception:
                self.logger.error(traceback.format_exc())
                return False

if __name__ == "__main__":
    app_name = "云闪付签到"
    app_env_name = "YSF_CREDENTIALS"
    local_script_name = os.path.basename(__file__)
    local_version = '2024.10.24'
    run = Run(app_name=app_name,
              app_env_name=app_env_name)
    run.main()
