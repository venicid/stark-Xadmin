from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class App01Config(AppConfig):
    name = 'app01'

    # 程序启动时，扫描app下得指定文件（starkadmin.py）并执行
    def ready(self):
        autodiscover_modules('starkadmin')