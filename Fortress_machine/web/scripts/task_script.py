# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
import paramiko, os
from repository import models
from concurrent.futures import ThreadPoolExecutor
from django import conf


class TaskTypeSolve(object):
    def __init__(self, task_id):
        self.task_id = task_id

    def execute(self):
        task_obj = models.Task.objects.get(id=self.task_id)
        pool = ThreadPoolExecutor(10)
        if task_obj.task_type == 'cmd':
            for task_log_obj in task_obj.tasklogdetail_set.all():
                pool.submit(self.ssh_cmd, task_log_obj)
        elif task_obj.task_type == 'file-transfer':
            task_content = task_obj.content
            for task_log_obj in task_obj.tasklogdetail_set.all():
                pool.submit(self.file_transfer, task_log_obj, task_content)
        pool.shutdown(wait=True)

    def ssh_cmd(self, task_log_obj):
        host_to_remote_user_obj = task_log_obj.host_to_remote_user
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                hostname=host_to_remote_user_obj.host.ip_addr,
                port=host_to_remote_user_obj.host.port,
                username=host_to_remote_user_obj.remote_user.username,
                password=host_to_remote_user_obj.remote_user.password,
                timeout=5
            )
            stdin, stdout, stderr = ssh.exec_command(task_log_obj.task.content)
            stdout_res = stdout.read()
            stderr_res = stderr.read()

            task_log_obj.result = stdout_res + stderr_res
            if stderr_res:
                task_log_obj.status = 2
            else:
                task_log_obj.status = 1
        except Exception as e:
            task_log_obj.result = e
            task_log_obj.status = 2
        task_log_obj.save()
        ssh.close()

    def file_transfer(self, task_log_obj, task_content):
        local_file_path, remote_file_path, task_type = task_content.split('|')
        host_to_user_obj = task_log_obj.host_to_remote_user
        try:
            t = paramiko.Transport((host_to_user_obj.host.ip_addr, host_to_user_obj.host.port))
            t.connect(
                username=host_to_user_obj.remote_user.username,
                password=host_to_user_obj.remote_user.password
            )
            sftp = paramiko.SFTPClient.from_transport(t)
            if task_type == 'post':
                # 本地至远程-->上传文件
                sftp.put(local_file_path, remote_file_path)
                result = '文件从本地路径[{local_file_path}]至远程主机路径[{remote_file_path}]上传成功'.format(
                    local_file_path=local_file_path, remote_file_path=remote_file_path
                )
            else:
                # 从远程主机下载文件
                download_file_path = os.path.join(conf.settings.DOWNLOAD_DIR, str(task_log_obj.id))
                if not os.path.isdir(download_file_path):
                    os.mkdir(download_file_path)
                file_name = remote_file_path.split('/')[-1]
                sftp.get(remote_file_path, os.path.join(download_file_path, file_name))
                result = '文件从远程主机路径[{remote_file_path}]下载文件[{file_name}]到本地路径[{download_file_path}]下载成功'.format(
                    remote_file_path=remote_file_path, file_name=file_name, download_file_path=download_file_path
                )
            task_log_obj.status = 1
            t.close()
        except Exception as e:
            task_log_obj.status = 2
            result = e
        task_log_obj.result = result
        task_log_obj.save()


def execute_from_command(argv=None):
    obj = TaskTypeSolve(argv[1] or '')
    obj.execute()