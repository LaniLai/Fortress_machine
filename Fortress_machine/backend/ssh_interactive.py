# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
from repository import models
from django.contrib.auth import authenticate
from backend import paramiko_ssh


class AutoSSH(object):
    """
    堡垒机交互界面
    """
    def __init__(self, callback):
        self.callback = callback
        self.models = models

    def auth(self):
        """
        登陆堡垒机
        :return:
        """
        count = 0
        while count < 3:
            username = input('堡垒机\n账号>>>')
            password = input('密码>>>')
            user_obj = authenticate(username=username, password=password)
            if not user_obj:
                count += 1
                continue
            self.user_obj = user_obj
            return True

    def interactive(self):
        if self.auth():
            print('登陆成功...', )
            while True:
                host_group_list = self.user_obj.host_groups.all()
                for index, host_group_obj in enumerate(host_group_list):
                    print(
                        '{0}.\t{1} [{2}]'.format(
                            index, host_group_obj.name, host_group_obj.host_to_remote_users.count()
                        )
                    )
                    print('z.\t未分组[%s]' % self.user_obj.host_to_remote_users.count())
                    choice = input('选择主机组>>>').strip()
                    if choice.isdigit():
                        choice = int(choice)
                        selected_host_group = host_group_list[choice]
                    elif choice.lower() == 'z':
                        selected_host_group = self.user_obj

                    while True:
                        for index, host in enumerate(selected_host_group.host_to_remote_users.all()):
                            print(
                                '{0}.\t{1}'.format(index, host)
                            )
                        choice = input('选择登陆的主机>>>').strip()
                        if choice.lower() == 'q':
                            break
                        elif choice.isdigit():
                            choice = int(choice)
                            selected_host = selected_host_group.host_to_remote_users.all()[choice]
                            print('正在连向主机 %s' % selected_host)
                            paramiko_ssh.ssh_connect(self, selected_host)
                            

