# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author CHERWIN✨✨✨
# @Modify qianfanguojin✨✨✨ @2024.09.01
# -------------------------------
# cron "27 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('霸王茶姬小程序')

import os
import requests
import time
import urllib3
import hashlib
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

if os.path.isfile('notify.py'):
    from notify import send
    print("加载通知服务成功！")
else:
    print("加载通知服务失败!")
send_msg = ''
one_msg=''
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
        self.token_ck = split_info[0]
        self.token_uid = split_info[1]
        self.index = index + 1
        Log(f"\n---------开始执行第{self.index}个账号>>>>>")
        self.s = requests.session()
        self.s.verify = False

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f) XWEB/8555',
            'work-wechat-userid': '',
            'multi-store-id': '',
            'gdt-vid': '',
            'qz-gtd': '',
            'scene': '1006',
            'Qm-From': 'wechat',
            'store-id': '49006',
            'Qm-User-Token': self.token_ck,
            'channelCode': '',
            'Qm-From-Type': 'catering',
            'promotion-code': '',
            'work-staff-name': '',
            'work-staff-id': '',
            'Accept': 'v=1.0',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'Referer': 'https://servicewechat.com/wxafec6f8422cb357b/87/page-frame.html'
        }
        self.s.headers.update(self.headers)
        self.appid = 'wxafec6f8422cb357b'
        self.activity_id='947079313798000641'
        self.store_id='49006'
        self.timestamp=int(time.time() * 1000)
        self.sign_str=self.getSign()
    def getSign(self):
        # 反转 activity_id
        reversed_activity_id = self.activity_id[::-1]

        # 构建参数对象
        params = {
            'activityId': self.activity_id,
            'sellerId': self.store_id if self.store_id is not None else None,
            'timestamp': self.timestamp,
            'userId': self.token_uid
        }

        # 按键排序并构建查询字符串
        sorted_params = sorted(params.items())
        query_string = '&'.join(f'{key}={value}' for key,
                                value in sorted_params if value is not None)
        query_string += f'&key={reversed_activity_id}'

        # 生成 MD5 哈希
        md5_hash = hashlib.md5(query_string.encode()).hexdigest().upper()

        return md5_hash
    def personal_info(self):
        personal_info_valid = False

        try:
            # 请求的参数
            params = {'appid': self.appid}

            # 发送GET请求
            response = self.s.get('https://webapi.qmai.cn/web/catering/crm/personal-info', json=params)
            result = response.json()

            # 检查请求是否成功
            if result.get('code','-1') == '0':
                personal_info_valid = True
                # 提取个人信息
                mobile_phone = result['data']['mobilePhone'] if 'data' in result and 'mobilePhone' in result[
                    'data'] else None
                self.mobile_phone = mobile_phone[:3] + "*" * 4 + mobile_phone[7:]
                self.name = result['data']['name'] if 'data' in result and 'name' in result['data'] else None

                Log(f"账号[{self.index}]登陆成功！\n用户名：【{self.name}】 \n手机号：【{self.mobile_phone}】")
            else:
                # 如果请求不成功，则打印错误信息
                message = result.get('message', '')
                Log(f'登录失败: {message}')

        except Exception as e:
            # 捕获任何异常并打印
            print(e)

        finally:
            # 最终返回请求是否成功的标志
            return personal_info_valid

    def user_sign_statistics(self):
        try:

            json_data = {
                'activityId': self.activity_id,
                'appid': self.appid
            }

            # Send the POST request
            response = self.s.post('https://webapi.qmai.cn/web/cmk-center/sign/userSignStatistics', json=json_data)
            result = response.json()
            status_code = response.status_code

            # Check if the request was successful
            if result.get('code', status_code) == 0:
                data = result.get('data', {})
                sign_days = data.get('signDays', '')
                sign_status = data.get('signStatus', 0) == 1
                Log(f'新版签到今天{"已" if sign_status else "未"}签到, 已连续签到{sign_days}天')
                if not sign_status:
                    self.take_part_in_sign()
                return sign_status, sign_days
            else:
                message = result.get('message', '')
                Log(f'查询新版签到失败: {message}')
                return False, 0
        except Exception as e:
            print(e)
            return False, 0

    def take_part_in_sign(self):
        try:
            json_data = {
                'activityId': self.activity_id,
                'storeId': self.store_id,
                'timestamp': self.timestamp,
                'signature': self.sign_str,
                'appid': self.appid
            }
            response = self.s.post('https://webapi.qmai.cn/web/cmk-center/sign/takePartInSign', json=json_data)
            result = response.json()
            status_code = response.status_code

            if result.get('code', status_code) == 0:
                data = result.get('data',{})
                rewardDetailList = data.get('rewardDetailList',[{}])
                if rewardDetailList:
                    rewardName = rewardDetailList[0].get('rewardName','')
                    sendNum = rewardDetailList[0].get('sendNum','')
                    Log(f'新版签到成功，获得【{sendNum}】{rewardName}')
                    return True
                else:
                    Log(f'签到失败：【{result.get("message","")}】')
                    return True
            else:
                message = result.get('message', '')
                Log(f'新版签到失败: {message}')
                return False
        except Exception as e:
            print(e)
            return False

    def points_info(self):
        try:
            json_data = {
                'appid': self.appid
            }

            response = self.s.post('https://webapi.qmai.cn/web/catering/crm/points-info', json=json_data)
            result = response.json()
            status_code = response.status_code

            if result.get('code', status_code) == '0':
                data = result.get('data', {})
                soon_expired_points = data.get('soonExpiredPoints', 0)
                total_points = data.get('totalPoints', 0)
                expired_time = data.get('expiredTime', '')

                if soon_expired_points:
                    Log(f'有【{soon_expired_points}】积分将于（ {expired_time}）过期')

                Log(f'当前积分: 【{total_points}】')
                return total_points, soon_expired_points, expired_time
            else:
                message = result.get('message', '')
                Log(f'查询积分失败: {message}')
                return None
        except Exception as e:
            print(e)
            return False

    def main(self):
        if not self.personal_info() :
            Log("用户信息无效，请更新CK")
            #self.sendMsg()
            return False
        self.user_sign_statistics()
        self.points_info()
        return True

    # def sendMsg(self, help=False):
    #     if self.send_UID:
    #         push_res = CHERWIN_TOOLS.wxpusher(self.send_UID, one_msg, APP_NAME, help)
    #         print(push_res)


def down_file(filename, file_url):
    print(f'开始下载：{filename}，下载地址：{file_url}')
    try:
        response = requests.get(file_url, verify=False, timeout=10)
        response.raise_for_status()
        with open(filename + '.tmp', 'wb') as f:
            f.write(response.content)
        print(f'【{filename}】下载完成！')

        # 检查临时文件是否存在
        temp_filename = filename + '.tmp'
        if os.path.exists(temp_filename):
            # 删除原有文件
            if os.path.exists(filename):
                os.remove(filename)
            # 重命名临时文件
            os.rename(temp_filename, filename)
            print(f'【{filename}】重命名成功！')
            return True
        else:
            print(f'【{filename}】临时文件不存在！')
            return False
    except Exception as e:
        print(f'【{filename}】下载失败：{str(e)}')
        return False

# def import_Tools():
#     global CHERWIN_TOOLS,ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode
#     import CHERWIN_TOOLS
#     ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode = CHERWIN_TOOLS.main(APP_NAME, local_script_name, ENV_NAME,local_version)
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

if __name__ == '__main__':
    APP_NAME = '霸王茶姬小程序'
    ENV_NAME = 'BWCJ_CK'
    CK_NAME = 'qm-user-token@userId'
    CK_URL = "https://webapi2.qmai.cn/web/cmk-center/sign/takePartInSign"
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
    积分签到
✨ 抓包步骤：
    打开{APP_NAME}，如果已登录请先退出登录
    打开抓包工具
    授权登陆，手动执行一次签到
    抓包 {CK_URL}
    找请求头中的{CK_NAME.split("@")[0]}，复制里面的{CK_NAME.split("@")[0]}参数值
    找响应内容中的{CK_NAME.split("@")[1]}，复制里面的{CK_NAME.split("@")[1]}参数值
    参数示例："vaH3ixxxxxxxxxxxxx@9983xxx"
✨ 设置青龙变量：
    export {ENV_NAME}='{CK_NAME}'参数值,多账号#或&分割
✨ ✨ 注意：抓完CK没事儿别打开小程序，重新打开小程序请重新抓包
✨ 推荐cron：27 9 * * *
✨✨✨ @Author CHERWIN✨✨✨
✨✨✨ @Modify qianfanguojin ✨✨✨
''')
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.06'
    # if IS_DEV:
    #     import_Tools()
    # else:
    #     if os.path.isfile('CHERWIN_TOOLS.py'):
    #         import_Tools()
    #     else:
    #         if down_file('CHERWIN_TOOLS.py', 'https://github.com/CHERWING/CHERWIN_SCRIPTS/raw/main/CHERWIN_TOOLS.py'):
    #             print('脚本依赖下载完成请重新运行脚本')
    #             import_Tools()
    #         else:
    #             print('脚本依赖下载失败，请到https://github.com/CHERWING/CHERWIN_SCRIPTS/raw/main/CHERWIN_TOOLS.py下载最新版本依赖')
    #             exit()
    # print(TIPS)
    bwcj_ck = os.getenv('BWCJ_CK')
    if not bwcj_ck:
        print(f"未填写 {ENV_NAME} 变量\n青龙可在环境变量设置 {ENV_NAME}")
        exit()
    token = bwcj_ck
    tokens = ENV_SPLIT(token)
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        for index, info in enumerate(tokens):
            run_result = RUN(info, index).main()
            if not run_result: continue
        import notify
        if notify.send: notify.send(f'{APP_NAME}挂机通知', send_msg)
