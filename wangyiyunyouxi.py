# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 网易云游戏
# @Author qianfanguojin
# @Time 2024.10.21
# @Description
# ✨ 功能：
#       网易云游戏获取免费时长，包括 签到、看广告视频
# ✨ 抓包步骤：
#       1. 打开网易云游戏手机 APP 进入登录账号界面（如已登录请先退出登录），选择手机验证码登录，点击获取验证码
#       2. 打开抓包软件，在网易云游戏手机 APP中输入验证码登录，登录完成后，搜索 https://n.cg.163.com/api/v1/tokens
#          在响应体中找到 token值、encrypt值、user_id值
#       最后组装为: token;encrypt;user_id，注意是英文分号分隔
# ✨ 变量示例：
#     export WANGYIYUNYOUXI_CREDENTIALS='eyJ0xxxxhbGciOiJIUzI1NiJ9.eyJpYXxxxx;method:1,number:123456,timestamp:17222222,salt:22;63cxx'，多账号#或&分割
# -------------------------------
# cron "7 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('网易云游戏');
# -------------------------------
import traceback
import requests
from script_tools import BaseRun
import os
import base64
import string
import json
import time
import random
class WYYYXCrypt:
    offset = 0
    def parse_to_offset(encrypt_data):
        """
        根据输入的字符串输出计算偏移量 offset

        参数:
        encrypt_data (str): 输入的加密字符串，格式为 "key1:value1,key2:value2,..."

        返回:
        int: 计算得到的偏移量
        """
        # 获取加密字符串的随机部分，并存入cookie
        encrypted_split = WYYYXCrypt.cookie_set(WYYYXCrypt.random_split(encrypt_data))

        # 从cookie中获取存储的随机加密字符串
        cookie_value = WYYYXCrypt.cookie_get(encrypted_split)

        # 通过cookie值获取偏移量
        offset_value = WYYYXCrypt.get_offset2(cookie_value)
        WYYYXCrypt.offset = offset_value
        return offset_value

    # 以下为相关辅助函数的假设实现（仅示例）
    def random_split(encrypt_data):
        """
        将输入字符串按照逗号进行分割，提取每个分割项中的第二部分（以冒号分割），
        然后将提取的部分用 'd' 连接成一个新的字符串。

        参数:
        encrypt_data (str): 输入的加密字符串，格式为 "key1:value1,key2:value2,..."

        返回:
        str: 提取后的字符串，各部分用 'd' 连接。
        """
        # 先按逗号分割字符串，再对每个部分按冒号分割，取第二部分，用'd'连接
        return 'd'.join([part.split(":")[1] for part in encrypt_data.split(",")])

    def cookie_set(data):
        """
        将输入字符串的每个字符转换为其对应的ASCII值，并与随机生成的字符串组合，
        然后用 '-' 连接成一个新的字符串。

        参数:
        data (str): 输入的字符串。

        返回:
        str: 处理后的字符串，字符的ASCII值与随机字符串组合。
        """
        # 将输入字符串拆分成字符列表
        char_list = list(data)

        # 对每个字符进行处理，将其ASCII值和随机字符串组合
        processed_chars = [
            f"{ord(char)}-{WYYYXCrypt.random_string()}" for char in char_list
        ]

        # 将处理后的字符列表用'-'连接成一个字符串
        return "-".join(processed_chars)

    def random_string():
        """
        生成一个包含两位小写字母和数字的随机字符串。

        返回:
        str: 随机生成的两位字符串。
        """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=2))

    def cookie_get(data):
        """
        从输入的经过编码的字符串中提取出每个字符的 ASCII 值，并将这些 ASCII 值转换为字符，
        最终组合成原始的字符串。

        参数:
        data (str): 输入的经过编码的字符串，格式为 "ASCII-随机串-ASCII-随机串-...".

        返回:
        str: 解码后的原始字符串。
        """
        # 如果输入数据存在，则按 '-' 分割，否则返回空列表
        split_data = data.split("-") if data else []

        # 过滤出原始的ASCII值部分（偶数位置的元素），并将其转换为字符
        ascii_values = [int(split_data[i]) for i in range(0, len(split_data), 2)]

        # 将ASCII值列表转换为字符串
        return ''.join([chr(value) for value in ascii_values])

    def get_offset2(data):
        """
        处理输入字符串，将其按 'd' 分割，转换为整数后，调用 get_offset 方法
        来计算偏移量。

        参数:
        data (str): 输入的字符串，格式为 "num1dnum2dnum3...".

        返回:
        int: 计算得到的偏移量。
        """
        # 将输入字符串按 'd' 分割，转换为整数
        numbers = [int(part) for part in data.split("d")]

        # 调用 get_offset 函数，传入分割后的整数列表（去掉第一个元素）
        return WYYYXCrypt.get_offset(*numbers[1:])

    def get_offset(e, t, i):
        """
        计算偏移量，根据公式 (e | t) % 256 + i。

        参数:
        e (int): 第一个整数。
        t (int): 第二个整数。
        i (int): 第三个整数。

        返回:
        int: 计算得到的偏移量。
        """
        return (e | t) % 256 + i

    def offset_out(base64_string):
        """
        对 Base64 编码的字符串进行解码，并通过给定的 offset 偏移量恢复原始字符。

        参数:
        offset (int): 用来解码的偏移量，与编码时使用的偏移量相同。
        base64_string (str): 经过 Base64 编码的字符串。

        返回:
        str: 解码并恢复的原始字符串。
        """
        # 从 Base64 字符串解码为字节数组
        byte_array = base64.b64decode(base64_string)
        # 用于存储恢复后的 ASCII 值
        ascii_data = []
        # 对每个字节进行偏移运算，恢复原始的字节值
        for byte in byte_array:
            ascii_data.append((byte - WYYYXCrypt.offset) % 256)
        # 将 ASCII 值转换为字符并拼接成字符串
        return ''.join(chr(num) for num in ascii_data)

    def offset_in(byte_array):
        """
        将输入的字节数组 `t` 中的每个字节加上整数 `e`，并对 256 取模，然后将结果编码为 Base64。

        参数:
        offset (int): 要加到每个字节上的整数。
        byte_array (bytes): 输入的字节数组。

        返回:
        str: 处理后的字节数组，经过 Base64 编码后的字符串。
        """
        # 将输入的字节数据转换为可修改的列表
        byte_array = bytearray(byte_array.encode('utf-8'))
        # 对每个字节加上整数 e，然后对 256 取模
        for n in range(len(byte_array)):
            byte_array[n] = (byte_array[n] + WYYYXCrypt.offset) % 256
        # 将处理后的字节数组编码为 Base64 字符串
        encoded_result = base64.b64encode(bytes(byte_array)).decode('utf-8')
        return encoded_result

class Run(BaseRun):

    def init_vars(self):
        self.base_url = "https://n.cg.163.com/"
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': "NetEaseCloudGame/2.8.8 (versionName:2.8.8.1;versionCode:2360;channel:xiaomi_new;sdk:34;device:Xiaomi,mondrian,23013RK75C;)",
            'Connection': "Keep-Alive",
            'Accept': "application/json",
            'Accept-Encoding': "gzip",
            #'Authorization': token,
            'X-Channel': "xiaomi_new",
            'X-Ver': "2360",
            'X-Source-Type': "xiaomi_new",
            'X-Platform': "2",
            'Content-Type': "application/octet-stream"
        }
    def process_var(self, info):
        token, encrypt, user_id = info.split(";")
        WYYYXCrypt.parse_to_offset(encrypt)
        self.run_user_id = user_id
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    #签到
    def sign(self):
        url = f'{self.base_url}/api/v2/sign-today'
        res = self.session.post(url=url)
        res_body = json.loads(WYYYXCrypt.offset_out(res.text))
        if res.status_code == 200:
            self.logger.info(f"✅ 签到成功")
            return True
        else:
            self.logger.debug(res_body)
            self.logger.info(f"ℹ️  {res_body.get('errmsgcn')}")
            return False
    #看广告
    def watch_ad(self):
        #获取广告信息
        url = f"{self.base_url}/api/v2/ads/get_info"
        params = {
            #'device_id': "ef77c58f82121928",
            'ads_platform_idx': "1",
            'scene_value': "sign_ads"
        }
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            self.logger.error(f"❌ 获取广告信息失败")
            return False
        ad_info = json.loads(WYYYXCrypt.offset_out(response.text))
        ads_id = ad_info.get("ads_id")
        scene_value = ad_info.get("scene_value")
        self.logger.debug(f"共 {ad_info['limit_times']} 次机会, 已使用 {ad_info['user_times']} 次")
        if ad_info['user_times'] == ad_info['limit_times']:
            self.logger.info(f"ℹ️  今日广告次数已用完")
            return False
        for i in range(ad_info['limit_times'] - ad_info['user_times']):
            self.logger.debug(f"开始看第 {ad_info['user_times'] + i + 1} 次广告")
            #2获取广告完成密钥（随机码）
            url = f"{self.base_url}/api/v2/one_submit_ticket"
            params = {
                'business_type': "1"
            }
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                self.logger.error(f"❌ 获取广告完成密钥失败")
                return False
            random_text = json.loads(WYYYXCrypt.offset_out(response.text))["random_text"]
            self.logger.debug(f"广告随机码：{random_text}")
            #3完成看广告
            url = f"{self.base_url}/api/v2/ads/give_ad_reward"
            ori_payload = {
                #"device_id": "ef77c58f82121928",
                "random_text": random_text,
                "ads_id": ads_id,
                "ads_platform_idx": 1,
                "scene_value": scene_value,
                "status": 1
            }
            origin_payload_str = json.dumps(ori_payload,separators=(",",":"))
            payload = WYYYXCrypt.offset_in(origin_payload_str)
            response = self.session.post(url, data=payload)
            ad_result = json.loads(WYYYXCrypt.offset_out(response.text))
            if response.status_code != 200:
                self.logger.debug(f"{ad_result.get('errmsgcn')}")
                self.logger.error(f"❌ 看广告失败")
                return False
            if not ad_result.get('reward_val'):
                self.logger.debug(f"{ad_result}")
                return False
            self.logger.info(f"✅ 看广告成功，获得 {ad_result.get('reward_val')/60} 分钟时长")
            time.sleep(10)
    def process(self):
        self.logger.info(f"当前版本：{local_version}")
        if self.app_env_infos:
            self.logger.info(f"\n=======\t共获取到 {len(self.app_env_infos)} 个账号")
        else:
            return
        for index, info in enumerate(self.app_env_infos):
            try:
                self.logger.info(f"\n=======\t开始执行第 {index + 1} 个账号")
                self.logger.info(f"\n==> 处理脚本必要的变量")
                self.process_var(info)
                self.logger.info(f"\n==> 账号ID: {self.run_user_id}")
                self.logger.info(f"\n==> 签到")
                self.sign()
                self.logger.info(f"\n==> 看广告")
                self.watch_ad()
                return True
            except Exception:
                self.logger.error(traceback.format_exc())
                return False


if __name__ == "__main__":
    app_name = "网易云游戏"
    app_env_name = "WANGYIYUNYOUXI_CREDENTIALS"
    local_script_name = os.path.basename(__file__)
    local_version = '2024.10.22'
    run = Run(app_name=app_name,
              app_env_name=app_env_name)
    run.main()
