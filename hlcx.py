# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 哈啰出行
# @Author qianfanguojin
# @Time 2024.09.01
# -------------------------------
# 软件名称：哈啰
# 奖励：积攒奖励金可换手机话费重置抵用券
# 抓包位置：首页 福利中心 查看更多 抓包 api.hellobike.com/api?urser 请求里面的 TOKEN
# 定时 0 8 * * *
# export HALUO_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# cron "1 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('哈啰签到');
import os
import json
import requests
import time
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

def RANDOM_DELAY_RUN(min_delay=60, max_delay=120):
    import random
    delay = random.uniform(min_delay, max_delay)
    Log(f"随机延迟{delay}秒")
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
    def __init__(self, info, index):
        self.index = index + 1
        Log(f"\n======== ▷ 第 {self.index} 个账号 ◁ ========")
        self.s = requests.session()
        self.s.verify = False
        self.hl_token = info
        self.headers = {
            'content-type': 'application/json'
        }

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
            return response.json()
        except requests.RequestException as e:
            print(f"请求异常: {e}")
            return None
    #签到
    def sign(self):
        sign_url = 'https://api.hellobike.com/api?common.welfare.signAndRecommend'
        sign_data = json.dumps({
            "from": "h5",
            "systemCode": 62,
            "platform": 4,
            "version": "6.46.0",
            "action": "common.welfare.signAndRecommend",
            "token": self.hl_token,
            "pointType": 1
        })
        # 签到操作
        sign_response = self.request_json('POST', sign_url, data=sign_data)
        if sign_response.get("data"):
            did_sign_today = sign_response['data']['didSignToday']
            bounty_count_today = sign_response['data']['bountyCountToday']
            Log(f'✅ 今日签到成功 金币+{bounty_count_today}' if did_sign_today else '❌ 今日未签到成功')
        else:
            Log(f'🚫 {sign_response.get("msg")}')
            Change_status("出错")

    def get_person_info(self,end=False):
        point_info_url = 'https://api.hellobike.com/api?user.taurus.pointInfo'
        point_info_data = json.dumps({
            "from": "h5",
            "systemCode": 61,
            "platform": 4,
            "version": "6.46.0",
            "action": "user.taurus.pointInfo",
            "token": self.hl_token,
            "pointType": 1
        })
        coupon_info_url = 'https://api.hellobike.com/api?user.wallet.coupon'
        coupon_info_data = json.dumps({
            "from": "h5",
            "systemCode": 62,
            "platform": 4,
            "version": "6.46.0",
            "action": "user.wallet.coupon",
            "token": self.hl_token,
        })
        # 查询奖励金操作
        point_info_response = self.request_json('POST', point_info_url, data=point_info_data)
        coupon_info_response = self.request_json('POST', coupon_info_url, data=coupon_info_data)
        if point_info_response:
            points = point_info_response['data']['points']
            Log(f"\n账号 {self.index} 可用奖励金为 {points}")
        reward = ''
        if coupon_info_response:

            for coupon in coupon_info_response['data']['couponList']:
                coupon_name = coupon['couponName']
                coupon_end_date = coupon['endDate']
                reward += f"  {coupon_name} 过期时间 {coupon_end_date}\n"
        Log(f"\n账号 {self.index} 可用优惠券:\n{reward}")
    #看广告视频
    def watch_video(self):
        task_list_url = 'https://marketingapi.hellobike.com/api?mars.task.showTaskList'
        task_list_data = json.dumps({
            "from": "h5",
            "systemCode": 62,
            "platform": 4,
            "version": "6.71.6",
            "action": "mars.task.showTaskList",
            "token": self.hl_token,
            "channelId": 4,
            "sceneNameEn": "platform_points",
            "subSceneNameEn": "platform_points_pointshp",
            "taskStatusList": [
                "INIT",
                "RUNNING"
            ],
            "queryUnrewardedTasks": 'true',
            # "adCode": "310115",
            # "cityCode": "021",
            # "longitude": 121.560449,
            # "latitude": 31.18883
        })
        # 查询任务列表
        task_list_response = self.request_json('POST', task_list_url, data=task_list_data)
        task_list_res_data = task_list_response.get('data')
        for task in task_list_res_data['taskList']:
            status = 0
            if task['mainTitle'] == '激励视频-任务1':
                if task['taskStatus'] == 'FINISHED' or task['taskStatus'] == 'RUNNING':
                    self.task_code = task['taskCode']
                    self.task_guid = task['taskGuid']
                    self.task_group_code = task['taskGroupCode']
                    self.offer_worth = task['offerWorth']
                    status = 1
                elif task['taskStatus'] == 'INIT':
                    self.pre_task_code = task['taskCode']
                    self.pre_task_group_code = task['taskGroupCode']

                #领取任务
                # if status == 0:
                #     task_video_accept = 'https://marketingapi.hellobike.com/api?mars.task.acceptTaskList'
                #     task_video_accept_data = json.dumps({
                #         "from": "h5",
                #         "systemCode": 62,
                #         "platform": 4,
                #         "version": "6.71.6",
                #         "action": "mars.task.acceptTaskList",
                #         "token": self.hl_token,
                #         "channelId": 4,
                #         "sceneNameEn": "platform_points",
                #         "subSceneNameEn": "platform_points_pointshp",
                #         # "adCode": "310115",
                #         # "cityCode": "021",
                #         # "longitude": 121.560449,
                #         # "latitude": 31.18883,
                #         "taskList": [
                #             {
                #             "taskCode": self.pre_task_code,
                #             "taskGroupCode": self.pre_task_group_code
                #             }
                #         ]
                #     })
                #     task_video_accept_response = self.request_json('POST', task_video_accept, data=task_video_accept_data)
                #     task_video_accept_res_data = task_video_accept_response.get('data')
                #     if task_video_accept_res_data:
                #         task_video_reward = task_video_accept_res_data['taskList'][0]
                #         self.pre_task_guid = task_video_reward['taskGuid']


                #领取奖励
                receive_reward_url = 'https://marketingapi.hellobike.com/api?mars.offer.receiveAward'
                receive_award_data = json.dumps({
                    "from": "h5",
                    "systemCode": 62,
                    "platform": 4,
                    "version": "6.71.6",
                    "action": "mars.offer.receiveAward",
                    "token": self.hl_token,
                    "channelId": 4,
                    "taskGuid": self.task_guid,
                    "taskGroupCode": self.task_group_code
                })
                receive_award_response = self.request_json('POST', receive_reward_url, data=receive_award_data)
                if receive_award_response.get('code') == 0:
                    Log(f"✅ 领取奖励金成功 + {self.offer_worth}")
    def main(self):
        try:
            Log('\n==>💥 签到')
            self.sign()
            self.get_person_info(True)
            #未实现
            #Log('\n==>📺 看广告')
            #self.watch_video()
        except Exception as e:
            Change_status("出错")
            Log(f"！！！执行异常: {str(e)}")
            return False








if __name__ == '__main__':
    APP_NAME = '哈啰出行'
    ENV_NAME = 'HALUO_TOKEN'
    CK_NAME = 'token值'
    CK_EX = 'ee7acxxxx'
    CK_URL = 'api.hellobike.com/api?urser'
    print(f'''
✨✨✨ {APP_NAME} 签到✨✨✨
✨ 功能：
    {APP_NAME} 签到
✨ 抓包步骤：
    打开抓包工具
    打开 {APP_NAME} APP/小程序
    找 {CK_URL} 请求头中 {CK_NAME}
✨ 设置青龙变量：
    export {ENV_NAME}='{CK_NAME}'参数值，多账号#或&分割
    示例：export {CK_EX}
✨ 推荐cron：0 0 8 * * *
✨✨✨ @Modify qianfanguojin ✨✨✨
''')
    if not IS_DEV:
        RANDOM_DELAY_RUN()
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.12'
    token = ''
    ENV = os.getenv(ENV_NAME)
    token = ENV if ENV else token
    if not token:
        Log(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入token =''")
        exit()
    tokens = ENV_SPLIT(token)

    print(f"{APP_NAME}共获取到{len(tokens)}个账号")

    for i, token in enumerate(tokens):

        RUN(token, i).main()

    # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()

    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
