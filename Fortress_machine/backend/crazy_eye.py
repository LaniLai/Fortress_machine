# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer


class ArgvHandler(object):
    """
    接收用户参数并执行相应功能
    """
    def __init__(self, sys_argv):
        self.sys_argv = sys_argv

    def call(self):
        if len(self.sys_argv) == 1:
            self.help_msg()
        if hasattr(self, self.sys_argv[1]):
            func = getattr(self, self.sys_argv[1])
            func()
        else:
            self.help_msg('输入的 %s 方法可能不存在' %self.sys_argv[1])

    def help_msg(self, error_msg=''):
        msg = """
            {error_msg}
            run   启动用户交互程序
        """.format(error_msg=error_msg)
        exit(msg)

    def run(self):
        """
        通过SSH方式
        启动用户交互程序
        """
        from backend import ssh_interactive
        obj = ssh_interactive.AutoSSH(self)
        obj.interactive()




