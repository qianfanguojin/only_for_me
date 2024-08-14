# -*- coding: utf-8 -*-
"""
cron: 16 19 * * *
new Env('OpenI算力积分签到');
"""



import requests
import os
from http.cookies import SimpleCookie
import time


def response_json(method, url, cookie=None, params=None):
    """
    发起请求获取json响应

    Args:
        url (_type_): 请求url
        cookie (_type_, optional): 请求的cookie. Defaults to None.
        params (_type_, optional): 请求的参数. Defaults to None.

    Returns:
        _type_: json响应
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.request(method,url, headers=headers, cookies=cookie, params=params)
        response.raise_for_status()  # 如果响应状态码不是 200-299，会引发 HTTPError
        return {'status': 'success', 'data': response.json()}
    except requests.RequestException as e:
        return {'status': 'error', 'error': str(e), 'response': response.text if response else 'No response'}

def restart(cookie):
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/restart"
    task = get_tasks()[0]["task"]
    if task["status"] == "STOPPED":
        params = {
            "id": task["id"],
            "_csrf": cookie["_csrf"]
        }
        result = response_json("POST", url, params=params, cookie=cookie)
        if result['status'] == 'success':
            return result['data']['data']['status']
        else:
            raise Exception(f"！！！任务重启失败: {result['error']} - {result['response']}")
    else:
        return "任务未停止"

def stop(cookie):
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/stop"
    task = get_tasks()[0]["task"]
    if task["status"] in ("WAITING","RUNNING"):
        params = {
            "id": task["id"],
            "_csrf": cookie["_csrf"]
        }
        result = response_json("POST", url, params=params, cookie=cookie)
        if result['status'] == 'success':
            return result['data']['data']['status']
        else:
            raise Exception(f"！！！任务停止失败: {result['error']} - {result['response']}")
    else:
        return "任务未启动"

def get_tasks():
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/list"
    params = None
    result = response_json("GET", url, params=params)
    if result['status'] == 'success':
        return result["data"]['data']["tasks"]
    else:
        raise Exception(f"！！！获取任务列表失败: {result['error']} - {result['response']}")

def parse_cookie(cookie_str):
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    cookie_dict = {key: morsel.value for key, morsel in cookie.items()}
    return cookie_dict

def main(cookie):
    # 重新调试启动任务
    restart(cookie)
    # 延迟5秒停止任务
    time.sleep(5)
    # 停止任务
    stop(cookie)
    #api_url_base = "https://openi.pcl.ac.cn/api/v1/"
    # repo_owner_name = "qianfanguojin"
    # repo_name = "OpenI_Cloudbrain_Example"
    # task_name = "ai_task"



if __name__ == '__main__':
    os.environ['OPENI_COOKIE'] = "lang=zh-CN; i_like_openi=71b88f888ade1dcd; Hm_lvt_46149a0b61fdeddfe427ff4de63794ba=1723223571,1723357414,1723478646; gitea_awesome=qianfanguojin; gitea_incredible=5b6274b74c393ed43d6d64ef36c44af526ff2910439dffe2217288916e5eff280cef270a5ee7a770b7; _csrf=aew4GTaO5sCx5gDsdElyOmirbvI6MTcyMzU2NjUzNzU0MzM4MjE3NA; Hm_lpvt_46149a0b61fdeddfe427ff4de63794ba=1723480427"
    for cookie_str in os.getenv('OPENI_COOKIE').split("&"):
         #print(dc)
        cookie_dict = parse_cookie(cookie_str)
        main(cookie_dict)
        print(f"账号：{cookie_dict['gitea_awesome']} OpenI算力积分签到成功 ！！！")

