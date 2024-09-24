# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# Telegram 签到
# @Author qianfanguojin
# @Time 2024.09.15
# -------------------------------
# cron "18 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('TG 签到');

import os,sys
import time
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

if os.path.isfile('.env'):
    IS_DEV = True
    from dotenv import load_dotenv
    load_dotenv('.env')
else:
    IS_DEV = False
def RANDOM_DELAY_RUN(min_delay=60, max_delay=120):
    import random
    delay = random.uniform(min_delay, max_delay)
    Log(f"\n随机延迟{delay}秒\n")
    time.sleep(delay)
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
def Log(cont=''):
    global send_msg
    print(cont)
    if cont:
        send_msg += f'{cont}\n'
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
class RUN:
    def __init__(self, index, info, proxy):
        self.index = index + 1
        self.info = info
        self.proxy = proxy
    def init_var(self):
        split_info = self.info.split('@')
        self.api_id = int(split_info[0])
        self.api_hash = split_info[1]
        self.auth_string = split_info[2]
        split_proxy = self.proxy.split('@')
        self.proxy_type = split_proxy[0]
        self.proxy_host = split_proxy[1]
        self.proxy_port = int(split_proxy[2])
        self.proxy = (self.proxy_type, self.proxy_host, self.proxy_port)
        self.day_of_week = datetime.now().weekday()

    async def initialize_client(self):
        self.client = TelegramClient(StringSession(self.auth_string), self.api_id, self.api_hash, proxy=self.proxy)
        await self.client.start()

    async def handle_bot_interaction(self, req_entity, resp_entity,
                                     command, success_message, sleep_time=0):
        try:
            await self.client.send_message(req_entity, command)
            await asyncio.sleep(sleep_time)
            result = await self.client.get_messages(req_entity, wait_time=1, from_user=resp_entity)
            msg = f"{success_message}\n{result[0].message}"
            await self.client.send_read_acknowledge(req_entity)
            Log(msg)
        except Exception as e:
            Log(str(e))

    #Getfree
    async def handle_getfree_cloud(self):
        getfree_cloud_chat_entity = await self.client.get_entity('t.me/GetfreeCloud')
        getfree_cloud_bot_entity = await self.client.get_entity('t.me/GetfreeCloud_Bot')
        #每周二，周五，周日 执行升级
        if self.day_of_week in (1, 4, 6):
            return await self.handle_bot_interaction(getfree_cloud_chat_entity, getfree_cloud_bot_entity,
                                                '/upgrade@GetfreeCloud_Bot', '\n✅ Getfree Upgraded !!')
        else:
            return await self.handle_bot_interaction(getfree_cloud_chat_entity, getfree_cloud_bot_entity,
                                                '/checkin@GetfreeCloud_Bot', '\n====>GetfreeCloud\n✅ @GetfreeCloud_Bot Checked !!')
    #ikuuu vpn
    async def handle_ikuuu_vpn(self):
        ikuuu_vpn_bot_entity = await self.client.get_entity("t.me/iKuuuu_VPN_bot")
        return await self.handle_bot_interaction(ikuuu_vpn_bot_entity,ikuuu_vpn_bot_entity,
                                            '/checkin', '\n====>iKuuuu_VPN\n✅ @iKuuuu_VPN_bot Checked !!', sleep_time=5)

    #飞跃彩虹
    async def handle_feiyuexingkong_music(self):
        if self.day_of_week == 0:
            feiyuexingkong_music_chat_entity = await self.client.get_entity(-1002197507537)
            feiyuexingkong_music_bot_entity = await self.client.get_entity("t.me/xingkongmusic_bot")
            return await self.handle_bot_interaction(feiyuexingkong_music_chat_entity,
                                                feiyuexingkong_music_bot_entity,
                                                '签到', '\n====>飞跃星空音乐服\n✅ 飞跃星空音乐服群组签到成功 !!')
        else:
            Log("\n====>飞跃星空音乐服\n❌ 今天不是周一，跳过飞跃星空音乐服群组签到")
    async def main(self):
        try:
            Log(f"\n=======\t开始执行第 {self.index}个账号 \t=======")
            # 初始化变量
            Log(f"\n==> 变量准备")
            self.init_var()
            # 初始化客户端
            Log(f"\n==> 初始化 Client")
            await self.initialize_client()
            Log(f"\n==> 开始打卡")
            tasks  = (self.handle_getfree_cloud(),
                      self.handle_ikuuu_vpn(),
                      self.handle_feiyuexingkong_music())
            await asyncio.gather(*tasks)
            Log(f"\n=======\t第{self.index}个账号执行完毕\t=======")
            return True
        except Exception as e:
            Log(f"！！！执行异常: {str(e)}")
            return False
if __name__ == "__main__":
    APP_NAME = 'TG 签到'
    ENV_NAMES = ("TG_AUTH_INFO", "TG_PROXY")
    CK_NAMES = ('appid@apihash@AuthString','ip@port')
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
    {APP_NAME}签到，用于各种机场，公益服务保号
✨ 设置青龙变量：
    export {ENV_NAMES[0]}='{CK_NAMES[0]}' 参数值，多账号#或&分割。
    export {ENV_NAMES[1]}='{CK_NAMES[1]}' 代理
✨ 推荐cron：0 23 1 * * *
✨✨✨ @Author qianfanguojin ✨✨✨
''')
    if not IS_DEV:
        RANDOM_DELAY_RUN()

    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.23'
    ENV = {
        "TG_AUTH_INFO": "",
        "TG_PROXY": ""
    }
    for ENV_NAME in ENV_NAMES:
        if not os.getenv(ENV_NAME):
            print(f"未填写 {ENV_NAME} 变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方往 ENV 字典中填充 {ENV_NAME} 对应的值")
            exit()
        ENV[ENV_NAME] = os.getenv(ENV_NAME)
    tokens = ENV_SPLIT(ENV[ENV_NAMES[0]])
    proxy = ENV[ENV_NAMES[1]]
    SCRIPT_STATUS = "正常"
    if len(tokens) > 0:
        Log(f"\n=======\t共获取到 {len(tokens)} 个账号\t=======")
        for index, info in enumerate(tokens):
            obj = RUN(index, info, proxy)
            run_result = asyncio.run(obj.main())
            if not run_result:
                SCRIPT_STATUS = "异常"

    # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()

    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
