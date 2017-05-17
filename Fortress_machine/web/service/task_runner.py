# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

import os, sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CrazyEye.settings")
    try:
        import django
        django.setup()
        from web.scripts import task_script
        if len(sys.argv) == 1:
            exit()
        task_script.execute_from_command(sys.argv)
    except ImportError:
        raise ImportError(
            '模块导入可能出错了'
        )
