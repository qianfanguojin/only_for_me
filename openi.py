#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/08/14 23:47
# @Author  : qianfanguojin
"""
cron: 16 19 * * *
const $ = new Env('OpenI算力积分签到');
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
    try:
        # 重新调试启动任务
        restart(cookie)
        # 延迟5秒停止任务
        time.sleep(5)
        # 停止任务
        stop(cookie)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    # qinglong 内置推送

    #api_url_base = "https://openi.pcl.ac.cn/api/v1/"
    # repo_owner_name = "qianfanguojin"
    # repo_name = "OpenI_Cloudbrain_Example"
    # task_name = "ai_task"



if __name__ == '__main__':
    for cookie_str in os.getenv('OPENI_COOKIE').split("&"):
         #print(dc)
        cookie_dict = parse_cookie(cookie_str)
        result = main(cookie_dict)
        msg = result['message']
        if result['status'] == 'success':
            msg = f"账号：{cookie_dict['gitea_awesome']} OpenI算力积分签到成功 ！！！"
        print(msg)
        import notify
        notify.send("【OPENI算力积分】", msg)

