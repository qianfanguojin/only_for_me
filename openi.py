# 对网站发起请求
# 1. 通过requests库发起请求

import requests
import json
import os


# 通过requests库发起请求
def get_response_json(url, cookie=None, params=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, cookies=cookie, params=params)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        return None

def post_response_json(url, cookie=None, params=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.post(url, headers=headers, cookies=cookie, params=params)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        return None

def restart(cookie):
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/restart"
    params = {
        "id": get_task_id(cookie),
        "_csrf": "aew4GTaO5sCx5gDsdElyOmirbvI6MTcyMzU2NjUzNzU0MzM4MjE3NA"
    }
    result = post_response_json(url, params=params, cookie=cookie)
    if result:
        return result["data"]["status"]

def stop(cookie):
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/stop"
    params = {
        "id": get_task_id(cookie),
        "_csrf": "aew4GTaO5sCx5gDsdElyOmirbvI6MTcyMzU2NjUzNzU0MzM4MjE3NA"
    }
    result = post_response_json(url, params=params, cookie=cookie)
    if result:
        return result["data"]["status"]

def get_task_id(cookie):
    url = "https://openi.pcl.ac.cn/api/v1/qianfanguojin/OpenI_Cloudbrain_Example/ai_task/list"
    params = None
    result = get_response_json(url, params=params)
    if result:
        return result["data"]["tasks"][0]["task"]["id"]

def main(cookie):
    stop(cookie)
    api_url_base = "https://openi.pcl.ac.cn/api/v1/"
    # repo_owner_name = "qianfanguojin"
    # repo_name = "OpenI_Cloudbrain_Example"
    # task_name = "ai_task"



if __name__ == '__main__':
    os.environ['OPENI_COOKIE'] = "lang=zh-CN; i_like_openi=71b88f888ade1dcd; Hm_lvt_46149a0b61fdeddfe427ff4de63794ba=1723223571,1723357414,1723478646; gitea_awesome=qianfanguojin; gitea_incredible=5b6274b74c393ed43d6d64ef36c44af526ff2910439dffe2217288916e5eff280cef270a5ee7a770b7; _csrf=aew4GTaO5sCx5gDsdElyOmirbvI6MTcyMzU2NjUzNzU0MzM4MjE3NA; Hm_lpvt_46149a0b61fdeddfe427ff4de63794ba=1723480427"
    for dc in os.getenv('OPENI_COOKIE').split("&"):
         #print(dc)
        _check_items = [
            {
                "cookie": dc
            }
        ]
        for item in _check_items:
            response = main(item)
            print(response)
