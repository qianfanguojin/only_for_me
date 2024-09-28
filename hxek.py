# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# 鸿星尔克
# @Author qianfanguojin✨✨✨
# @Time 2024.09.01
# -------------------------------
# cron "5 11 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('鸿星尔克官方会员中心小程序')

import os
import random
import time
import time
import requests
import hashlib
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# import CHERWIN_TOOLS
# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)
#


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
        global one_msg
        one_msg = ''
        # memberId @ enterpriseId @ unionid @ openid @ wxOpenid
        split_info = info.split('@')
        len_split_info = len(split_info)
        if len_split_info < 2:
            print('变量长度不足，请检查变量')
            return False
        self.memberId = split_info[0]
        self.enterpriseId = split_info[1]
        # print(self.token)

        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            print('检测到设置了UID')
            print(last_info)
            self.send_UID = last_info
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': 'hope.demogic.com',
            'xweb_xhr': '1',
            'channelEntrance': 'wx_app',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/9129',
            'sign': self.enterpriseId,
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wxa1f1fa3785a47c7d/55/page-frame.html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.appid = 'wxa1f1fa3785a47c7d'
        self.defualt_parmas = {
            'memberId': self.memberId,
            'cliqueId': '-1',
            'cliqueMemberId': '-1',
            'useClique': '0',
            'enterpriseId': self.enterpriseId,
            'appid': self.appid,
            'gicWxaVersion': '3.9.16'
        }
        self.baseUrl = 'https://hope.demogic.com/gic-wx-app/'
        self.use_power_max = False

    def make_request(self, url, method='post', headers={}, data={}, params=None):
        if headers == {}:
            headers = self.headers
        try:
            if method.lower() == 'get':
                response = self.s.get(url, headers=headers, verify=False, params=params)
            elif method.lower() == 'post':
                response = self.s.post(url, headers=headers, json=data, params=params, verify=False)
            else:
                raise ValueError("不支持的请求方法❌: " + method)
            return response.json()
        except requests.exceptions.RequestException as e:
            print("请求异常❌：", e)
        except ValueError as e:
            print("值错误或不支持的请求方法❌：", e)
        except Exception as e:
            print("发生了未知错误❌：", e)

    def gen_sign(self):
        # appid = "wxa1f1fa3785a47c7d"
        secret = 'damogic8888'
        # 获取GMT+8的当前时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # timestamp = '2024-05-22 16:07:54'
        # 生成随机数
        random_int = random.randint(1000000, 9999999)
        # random_int = 4270745
        # 构建待加密字符串
        raw_string = f"timestamp={timestamp}transId={self.appid}{timestamp}secret={secret}random={random_int}memberId={self.memberId}"
        # 使用MD5进行加密
        md5_hash = hashlib.md5(raw_string.encode())
        sign = md5_hash.hexdigest()
        self.defualt_parmas['random'] = random_int
        self.defualt_parmas['sign'] = sign
        self.defualt_parmas['timestamp'] = timestamp
        self.defualt_parmas['transId'] = self.appid+timestamp

    def get_member_grade_privileg(self):
        act_name = '获取用户信息'
        Log(f'\n====== {act_name} ======')
        self.gen_sign()
        self.defualt_parmas['launchOptions'] = '{"path":"pages/points-mall/member-task/member-task","query":{},"scene":1256,"referrerInfo":{},"apiCategory":"default"}'

        url = f"{self.baseUrl}get_member_grade_privileg.json"
        response_user = self.make_request(url,'post',params=self.defualt_parmas)

        # 获取积分记录
        url = f"{self.baseUrl}integral_record.json"
        self.defualt_parmas['launchOptions'] = '{"path":"pages/member-center/personal-data/personal-data","query":{},"scene":1106,"referrerInfo":{},"mode":"default","apiCategory":"default"}'
        self.defualt_parmas['currentPage'] = 1
        self.defualt_parmas['pageSize'] = 20
        self.gen_sign()
        response_points = self.make_request(url,'post',params=self.defualt_parmas)
        response_points_info = response_points.get('response', {})
        accumulat_points = response_points_info.get('accumulatPoints', '')
        if response_user.get('errcode', -1) == 0:
            data = response_user.get('response', {})
            member = data.get('member', {})
            if member:
                phoneNumber = member.get('phoneNumber', '')
                phone = phoneNumber[:3]+'***'+phoneNumber[-4:]
                wxOpenid = member.get('openId', '')
                unionid = member.get('thirdUnionid', '')
                self.defualt_parmas['wxOpenid'] = wxOpenid
                self.defualt_parmas['unionid'] = unionid
                Log(f'✅{act_name}成功！')
                if accumulat_points:
                    Log(f'> 当前用户：【{phone}】已拥有的积分：{accumulat_points} ')
                    return True
                Log(f'> 当前用户：【{phone}】')
            return True
        elif response_user.get('errcode', -1) == 900001:
            Log(f'> 今天已签到✅')
            return False
        else:
            print(f'{act_name}失败❌：{response_user}')
            return False

    def member_sign(self):
        act_name = '签到'
        Log(f'\n====== {act_name} ======')
        self.gen_sign()
        self.defualt_parmas['launchOptions'] = '{"path":"pages/points-mall/member-task/member-task","query":{},"scene":1256,"referrerInfo":{},"apiCategory":"default"}'
        url = f"{self.baseUrl}member_sign.json"
        response = self.make_request(url,'post',params=self.defualt_parmas)
        if response.get('errcode', -1) == 0:
            res = response.get('response', {})
            memberSign = res.get('memberSign', {})
            integralCount = memberSign.get('integralCount', '')
            continuousCount = memberSign.get('continuousCount', '')
            points = res.get('points', '')
            Log(f'✅{act_name}成功！')
            Log(f'> 当前积分：【{points}】 连续签到：【{continuousCount}】天')
            return True
        elif response.get('errcode', -1) == 900001:
            Log(f'✅今天已签到')
            return False
        else:
            print(f'{act_name}失败❌：{response}')
            Change_status("异常")
            return False

    def main(self):
        Log(f"\n开始执行第{self.index}个账号--------------->>>>>")
        if self.get_member_grade_privileg():
            # random_delay()
            self.member_sign()

            return True
        else:
            Change_status("异常")
            return False


def random_delay(min_delay=1, max_delay=5):
    """
    在min_delay和max_delay之间产生一个随机的延时时间，然后暂停执行。
    参数:
    min_delay (int/float): 最小延时时间（秒）
    max_delay (int/float): 最大延时时间（秒）
    """
    delay = random.uniform(min_delay, max_delay)
    print(f">本次随机延迟： {delay:.2f} 秒.....")
    time.sleep(delay)





if __name__ == '__main__':
    APP_NAME = '鸿星尔克官方会员中心小程序'
    ENV_NAME = 'HXEK_COOKIE'
    CK_URL = 'hope.demogic.com请求头'
    CK_NAME = 'memberId@enterpriseId'
    CK_EX = 'ff80808xxxxxxxx@ff8080817xxxxxxx'
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨功能：
    {APP_NAME}积分签到
✨抓包步骤：
    打开{APP_NAME}
    授权登陆
    打开抓包工具
    找{CK_URL}{CK_NAME}
    参数示例：{CK_EX}
✨设置青龙变量：
    export {ENV_NAME}='{CK_NAME}参数值'多账号#或&分割
✨ ✨ 注意：抓完CK没事儿别打开小程序，重新打开小程序请重新抓包
✨ 推荐cron：5 11 * * *
✨✨✨ @Author CHERWIN ✨✨✨
✨✨✨ @Modify qianfanguojin ✨✨✨
''')
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
            run_result = RUN(infos, index).main()
            if not run_result: continue
        # if send: send(f'{APP_NAME}挂机通知', send_msg + TIPS_HTML)
        # 在LOAD_SEND中获取导入的send函数
    send = LOAD_SEND()

    # 判断send是否可用再进行调用
    if send:
        send(f'{APP_NAME}挂机通知【{SCRIPT_STATUS}】', send_msg)
    else:
        print('通知服务不可用')
