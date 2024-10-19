# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# OpenI 启智平台
# @Author qianfanguojin
# @Time 2024.09.07
# @Url https://openi.pcl.ac.cn/
# -------------------------------
# cron "16 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('OpenI算力积分签到');
# -------------------------------
APP_NAME = 'OpenI 启智社区'
ENV_NAME = 'OPENI_COOKIE'
# ✨✨✨ OpenI 启智社区签到✨✨✨
# ✨ 功能：
#       OpenI 启智社区I算力积分签到，积分可用于兑换算力时间
# ✨ 变量获取：
#       打开 https://openi.pcl.ac.cn, 登录账号，按 F12 打开开发者工具，找到 https://openi.pcl.ac.cn/user/login 请求的用户名和密码
#       新建一个仓库 repo，添加任意云脑任务，记录此 repo 名字
#       组装为：用户名@密码@测试仓库名
# ✨ 变量示例：
#       export ENV_NAME='user@password@repo'参数值，多账号#或&分割
# ✨✨✨ @Author qianfanguojin ✨✨✨

import requests
import re
import os
import time
import rsa,base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

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
        self.split_info = info.split('@')
        self.index = index + 1

    def init_var(self):
        self.user_name = ''
        self.password = ''
        self.repo = ''

        for i, info in enumerate(self.split_info):
            if i == 0:
                self.user_name = info
            elif i == 1:
                self.password = info
            elif i == 2:
                self.repo = info
        if self.user_name == '' or self.password == '' or self.repo == '':
            Log(f"！！！账号信息不完整: {self.user_name} - {self.repo}")
            Change_status("出错")
            return False
        Log(f"\n---------开始执行第{self.index}个账号：{self.user_name}>>>>>")
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.s.headers.update(self.headers)
        self.base_url = "https://openi.pcl.ac.cn"
        self.csrf= self.get_csrf_token()

    def response_json(self, method, url, params=None, data=None):
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
            response = self.s.request(method, url, headers=self.headers, params=params, data=data)
            response.raise_for_status()  # 如果响应状态码不是 200-299，会引发 HTTPError
            return {'status': 'success', 'data': response.json()}
        except requests.RequestException as e:
            return {'status': 'error', 'error': str(e), 'response': response.text if response else 'No response'}


    def issue_new_and_close(self):
        # 创建 3 个 issue
        Log(f"{self.user_name}/{self.repo} 开始创建任务")
        url = f"{self.base_url}/{self.user_name}/{self.repo}/issues/new"
        payload = {
            "_csrf": self.csrf,
            "title": "测试issue",
            "content": "测试issue",
            "ref": '',
            "search": '',
            "label_ids": '',
            "milestone_id": '',
            "assignee_ids": ''
        }
        for index in range(3):
            new_result = self.s.post(url, data=payload)
            if new_result.status_code == 200:
                Log(f"{self.user_name}/{self.repo} 创建第 {index + 1} 个任务成功")
            else:
                Log(f"！！！创建第 {index + 1} 个任务失败: {result['reason']}")
                Change_status("出错")
                return False
            time.sleep(2)
        # 删除创建的 3 个 issue
        Log(f"{self.user_name}/{self.repo} 关闭创建的任务")
        url = f"{self.base_url}/{self.user_name}/{self.repo}/issues?q=&type=all&sort=&state=open&labels=&milestone=0&assignee=0"
        result = self.s.get(url)
        soup = BeautifulSoup(result.text, "html.parser")
        issues = soup.find_all("div", class_="issue list")
        if not (issues and len(issues) > 0):
            Log(f"任务获取为空: {result['reason']}")
            Change_status("出错")
            return False
        inputs = issues[0].find_all("input")
        for index, input in enumerate(inputs[:3]):
            issue_id = input["data-issue-id"]
            url = f"{self.base_url}/{self.user_name}/{self.repo}/issues/status"
            payload = {
                "_csrf": self.csrf,
                "action": 'close',
                "issue_ids": issue_id,
                "is_add": '',
            }
            result = self.response_json("POST", url, data=payload)
            if result['status'] == 'success':
                Log(f"{self.user_name}/{self.repo} 关闭第 {index + 1} 个任务成功")
            else:
                Log(f"！！！关闭第 {index + 1} 个任务失败: {result['reason']}")
                Change_status("出错")
                return False
            time.sleep(2)
        # 获取已关闭的任务列表
        Log(f"{self.user_name}/{self.repo} 检查关闭的任务数量是否超标")
        url = f"{self.base_url}/{self.user_name}/{self.repo}/issues?q=&type=all&sort=&state=closed&labels=&milestone=0&assignee=0"
        result = self.s.get(url)
        soup = BeautifulSoup(result.text, "html.parser")
        element_a = soup.select(f'#issue-filters a[href="/{self.user_name}/{self.repo}/issues?q=&type=all&sort=&state=closed&labels=&milestone=0&assignee=0"]')
        issue_count = 0
        if len(element_a) > 0:
            element_a_text = element_a[0].get_text()
            #获取 element_a_text 标签内容中的数字部分
            match = re.search(r'\d+', element_a_text)
            if match:
                issue_count = int(match.group())
        if issue_count >= 100:
            Log(f"！！！任务数量超标: {issue_count}")
            Change_status("警告","关闭的任务数量大于等于100")
            return False
        Log(f"{self.user_name}/{self.repo} 目前关闭的任务数量为: {issue_count}")
        return True
    def restart(self):
        url = f"{self.base_url}/api/v1/{self.user_name}/{self.repo}/ai_task/restart"
        task = self.get_tasks()[0]["task"]
        try:
            if task["status"] == "STOPPED":
                params = {
                    "id": task["id"],
                    "_csrf": self.csrf
                }
                result = self.response_json("POST", url, params=params)
                if result['status'] == 'success':
                    Log(f"{self.user_name}/{self.repo} 下的 {task['display_job_name']} 任务重启成功")
                    return True
                else:
                    Log(f"！！！任务重启请求失败: {result['error']} - {result['response']}")
                    Change_status("出错")
                    return False
            else:
                Log("！！！任务未停止，无法执行重启命令")
                Change_status("出错")
                return False
        except requests.RequestException as e:
            Log(f"！！！任务重启异常: {str(e)}")
            Change_status("出错")
            return False

    def stop(self):
        url = f"{self.base_url}/api/v1/{self.user_name}/{self.repo}/ai_task/stop"
        task = self.get_tasks()[0]["task"]
        try:
            if task["status"] in ("WAITING","RUNNING"):
                params = {
                    "id": task["id"],
                    "_csrf": self.csrf
                }
                result = self.response_json("POST", url, params=params)
                if result['status'] == 'success':
                    Log(f"{self.user_name}/{self.repo} 下的 {task['display_job_name']} 任务停止成功")
                    return True
                else:
                    Log(f"！！！任务停止失败: {result['error']} - {result['response']}")
                    Change_status("出错")
                    return False
            else:
                Log("！！！任务未启动, 无法执行停止命令")
                Change_status("出错")
                return False
        except requests.RequestException as e:
            Log(f"！！！任务停止异常: {str(e)}")
            Change_status("出错")
            return False

    def get_tasks(self):
        url = f"{self.base_url}/api/v1/{self.user_name}/{self.repo}/ai_task/list"
        params = None
        result = self.response_json("GET", url, params=params)
        if result['status'] == 'success':
            return result["data"]['data']["tasks"]
        else:
            msg = f"！！！获取任务列表失败: {result['error']} - {result['response']}"
            Log(msg)
            Change_status("出错")
            raise msg

    def get_personal_info(self,end=False):
        url = f"{self.base_url}/reward/point/account"
        params = {"_csrf": self.csrf}
        result = self.response_json("GET", url, params=params)
        if result['status'] == 'success':
            data = result["data"]['Data']
            total_balance = data.get('Balance', 0)
            total_points = data.get('TotalEarned', 0)
            total_consumed = data.get('TotalConsumed', 0)
            if not end:
                Log(f'当前可用算力积分:【{total_balance}】，总获取算力积分:【{total_points}】，总消耗算力积分:【{total_consumed}】')
                return
            Log(f'【执行后】当前可用算力积分:【{total_balance}】，总获取算力积分:【{total_points}】，总消耗算力积分:【{total_consumed}】')
        else:
            msg = f"！！！获取用户信息失败: {result['error']} - {result['response']}"
            Log(msg)
            Change_status("出错")

    def get_csrf_token(self):

        # 加密的公钥
        publicKey="-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC8qOB41dNhDZyhdgiIxvCYv8fS\nkfWZOCWUZ3qhl//nMDz5RjemCxCQ2C3o63kbzWW6fEKRIWydhrVIWBu8eCEe7MfT\nYFe7IeOlwDH9mLqbMDzcLjFHphXNb2rRUii+PFJovdL9ys8utCDkWTSnP2G2x1RZ\nxUfxfQqoYkMaAEio0QIDAQAB\n-----END PUBLIC KEY-----";
        # 用指定的公钥使用 RSA 加密密码
        pub = rsa.PublicKey.load_pkcs1_openssl_pem(publicKey.encode())
        password_encrypt = rsa.encrypt(self.password.encode(), pub)
        password_base64 = base64.encodebytes(password_encrypt)


        # 获取第一阶段未授权的 csrf_token，用于登录网站
        home_url = self.base_url
        home_result = self.s.get(home_url, headers = self.headers)
        unauthorized_csrf_token = home_result.cookies.get("_csrf")
        if not (home_result.status_code == 200 and unauthorized_csrf_token):
            message = home_result.get('reason', '')
            Log(f'获取未授权的 csrf_token 失败: {message}')
            Change_status("出错")
            return False
        Log(f'获取未授权的 csrf_token 成功: {unauthorized_csrf_token}')
        login_url = f"{self.base_url}/user/login"
        payload = {
            "user_name": self.user_name,
            "password": password_base64,
            "_csrf": unauthorized_csrf_token
        }
        login_result = self.s.post(login_url, data=payload)
        csrf_token = login_result.cookies.get("_csrf")
        # 第二阶段获取到的 csrf_token 为空或者和未授权的 csrf_token 相同，说明登录失败
        if not (login_result.status_code == 200 and csrf_token and unauthorized_csrf_token != csrf_token):
            Log(f'获取授权的 csrf_token 失败 ！！')
            Change_status("出错")
            return False
        Log(f'获取授权的 csrf_token 成功: {csrf_token}')
        return csrf_token

    def main(self):
        try:
            # 初始化变量
            self.init_var()
            if self.csrf:
                # 获取执行前用户信息
                self.get_personal_info()
                # 创建和删除任务（Issue）
                self.issue_new_and_close()
                # 重新调试启动云脑任务
                self.restart()
                # 延迟5秒停止云脑任务
                time.sleep(5)
                # 停止云脑任务
                self.stop()
                # 获取执行后用户信息
                self.get_personal_info(end=True)
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
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.07'
    token = ''
    ENV = os.getenv('OPENI_COOKIE')
    token = ENV if ENV else token
    if not token:
        Log(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将环境变量填入token =''")
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


