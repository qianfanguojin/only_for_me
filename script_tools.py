import random
import time
from enum import Enum
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from abc import ABC, abstractmethod

urllib3.disable_warnings(InsecureRequestWarning)

class BaseRun(ABC):
    def __init__(self, app_name=None, app_env_name=None, app_env_infos=None):
        self.logger = self.ScriptLogger()
        self.tools = self.ScriptTool()
        self.app_name = app_name
        self.app_env_name = app_env_name
        self.app_env_infos = app_env_infos



    class ScriptTool:
        @staticmethod
        def env_split(env_str):
            if '\n' in env_str:
                hash_parts = env_str.split('\n')
                return (hash_parts)
            else:
                out_str = str(env_str)
                return ([out_str])
        @staticmethod
        def random_delay_run(min_delay=60, max_delay=120):
            delay = random.uniform(min_delay, max_delay)
            print(f"\n随机延迟{delay}秒\n")
            time.sleep(delay)
        @staticmethod
        def load_send():
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
            return False
        @staticmethod
        def dev():
            cur_path = os.path.abspath(os.path.dirname(__file__))
            env_file = cur_path + "/.env"
            if os.path.isfile(env_file):
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return True
            else:
                return False

    class ScriptLogger:
        class ScriptStatus(Enum):
            SUCCESS = "正常"
            FAILURE = "异常"
        '''日志记录器，用于记录日志并获取通知消息'''
        def __init__(self):
            self.notify_message = ""
            self.status = self.ScriptStatus.SUCCESS
        def print(self, one_message, append_line=True):
            if one_message:
                print(f"{one_message}")
                if append_line:
                    self.notify_message += f"{one_message}\n"
        def info(self, one_message):
            self.print(one_message)
        def error(self, one_message):
            self.status = self.ScriptStatus.FAILURE
            self.print(one_message)
        def debug(self, one_message):
            self.print(f"| DEBUG | - {one_message}", append_line=False)

        def get_notify_message(self):
            return self.notify_message
        def get_status(self):
            return self.status
    @abstractmethod
    def init_vars(self, index, info):
        """初始化数据，必须由子类实现"""
        pass

    @abstractmethod
    def process(self):
        """处理数据，必须由子类实现"""
        pass
    def notify(self):
        """发送通知，这是一个钩子方法，可以选择重写"""
        send = self.ScriptTool.load_send()
        if send:
            send(f'{self.app_name}挂机通知【{self.logger.status.value}】', self.logger.notify_message)
    def get_envinfo(self):
        if self.app_env_infos:
            return
        app_env_str = os.environ.get(self.app_env_name)
        if not app_env_str:
            self.logger.error(f"未填写 {self.app_env_name} 变量, 青龙可在环境变量设置 {self.app_env_name}")
        else:
            app_envs = self.tools.env_split(app_env_str)
            if len(app_envs) > 0:
                self.app_env_infos = app_envs
    # 模板方法，定义算法的框架
    def main(self, notify=True):
        if not self.tools.dev():
            self.tools.random_delay_run()
        self.get_envinfo()
        self.init_vars()
        self.process()
        if notify: self.notify()
