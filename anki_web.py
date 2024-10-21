# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# AnkiWeb 登录保活
# @Author qianfanguojin
# @Time 2024.10.21
# -------------------------------
# cron "19 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('AnkiWeb 登录保活');
# -------------------------------

import urllib3
from urllib3.exceptions import InsecureRequestWarning
import traceback
import requests
urllib3.disable_warnings(InsecureRequestWarning)
from script_tools import BaseRun
import os

class Run(BaseRun):

    def init_vars(self):
        self.headers = {
            "Content-Type": "application/octet-stream"
        }
        self.base_url = "https://ankiweb.net/"
        self.session = requests.Session()
    def process_var(self, info):
        username, password = info.split(";")
        text = f"{username}{password}".encode()
        text_array = bytearray(text)
        text_array.insert(0,17)
        text_array.insert(0,10)
        text_array.insert(19,6)
        text_array.insert(19,18)
        self.run_token = text_array

    def login(self):
        self.session.headers.update(self.headers)
        url = f"{self.base_url}svc/account/login"
        login_result = self.session.post(url, data=self.run_token)
        if login_result.status_code == 200:
            temp_refresh_token = login_result.text[5:]
            confirm_login_result = self.session.get(f"https://ankiuser.net/account/ankiuser-login?t={temp_refresh_token}")
            if confirm_login_result.status_code == 200:
                self.logger.info("✅ 登录成功！")
                return True
        self.logger.error("❌ 登录失败！！")
        return False
    def check_deck_list(self):
        url = f"{self.base_url}svc/decks/deck-list-info"
        data = bytearray([8,160,252,255,255,255,255,255,255,1])
        deck_list_result = self.session.post(url,data=data)
        if deck_list_result.status_code == 200:
            self.logger.info("✅ 获取卡片主页信息成功")
        else:
            self.logger.error("❌ 获取卡片主页信息失败")
    def process(self):
        self.logger.info(f"当前版本：{local_version}")
        if self.app_env_infos:
            self.logger.info(f"\n=======\t共获取到 {len(self.app_env_infos)} 个账号")
        else:
            return
        for index, info in enumerate(self.app_env_infos):
            try:
                self.logger.info(f"\n=======\t开始执行第 {index + 1} 个账号")
                self.logger.info(f"\n==> 处理账号密码")
                self.process_var(info)
                self.logger.info(f"\n==> 登录 AnkiWeb 账号")
                if self.login():
                    self.logger.info(f"\n==> 测试登录状态")
                    self.check_deck_list()
                return True
            except Exception:
                self.logger.error(traceback.format_exc())
                return False


if __name__ == "__main__":
    app_name = "AnkiWeb"
    app_env_name = "ANKIWEB_CREDENTIALS"
    local_script_name = os.path.basename(__file__)
    local_version = '2024.09.23'
    run = Run(app_name=app_name,
              app_env_name=app_env_name)
    run.main()
