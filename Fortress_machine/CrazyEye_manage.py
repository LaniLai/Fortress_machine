# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer


import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CrazyEye.settings")
    import django
    django.setup()

    from backend import crazy_eye
    interactive_obj = crazy_eye.ArgvHandler(sys_argv=sys.argv)
    interactive_obj.call()

