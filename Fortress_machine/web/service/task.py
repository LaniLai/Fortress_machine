# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
import json, subprocess
from repository import models
from django import conf
from django.http.request import QueryDict
from utils.response import BaseResponse


class TaskAnalysis(object):
    """ 
    任务处理
    """
    def __init__(self, request):
        self.request = request
        self.execute()

    def execute(self):
        self.task_give_away()

    def task_give_away(self):
        """
        任务解析、分发
        :return: 
        """
        # 获取任务数据
        post_data = json.loads(self.request.POST.get('postData'))
        execute_type = post_data.get('executeType')
        if hasattr(self, execute_type):
            cls_func = getattr(self, execute_type)
            cls_func(post_data)

    def cmd(self, post_data):
        """
        1、创建一条Task任务, 并初始化每台主机反馈结果
        2、触发任务且不阻塞，反馈给前端Task.id
        :param post_data: 执行数据（主机IDS, 命令）
        :return: 
        """
        self.init_create(post_data)

    def file(self, post_data):
        """
        1、文件分发
        2、创建一条Task任务, 并初始化每台主机反馈结果
        3、触发任务且不阻塞，反馈给前端Task.id
        :param post_data: 
        :return: 
        """
        self.init_create(post_data)

    def init_create(self, post_data):
        """
        
        :param post_data: 
        :return: 
        """
        execute_type = post_data.get('executeType')
        task_content = ''
        if execute_type == 'file':
            execute_type = 'file-transfer'
            task_content = '{local_file_path}|{remote_file_path}|{file_type}'.format(
                local_file_path=post_data.get('local_file_path'),
                remote_file_path=post_data.get('remote_file_path'),
                file_type=post_data.get('file_type')
            )
        elif execute_type == 'cmd':
            task_content = post_data.get('cmdText')

        self.task_obj = models.Task.objects.create(
            task_type=execute_type,
            content=task_content,
            user=self.request.user
        )
        selected_host_ids = post_data.get('selectedHostIds')
        # 初始化结果信息
        task_log_details = []
        for host_id in selected_host_ids:
            task_log_details.append(models.TaskLogDetail(
                task=self.task_obj,
                host_to_remote_user_id=host_id,
                result='初始化信息中...',
                status=0
            ))
        models.TaskLogDetail.objects.bulk_create(task_log_details)
        # 执行一段程序, 相当于另开一条进程, 批量连接远程主机取结果(IO任务型)
        task_script = 'python %s/web/service/task_runner.py %s' % (conf.settings.BASE_DIR, self.task_obj.id)
        subprocess.Popen(task_script, shell=True)


class TaskLogResult(object):

    @staticmethod
    def fetch_result(task_obj):
        response = BaseResponse()
        try:
            ret = {
                'task_id': task_obj.task_obj.id,
                'hosts_info': list(task_obj.task_obj.tasklogdetail_set.all().values(
                    'id',
                    'host_to_remote_user__host__ip_addr',
                    'host_to_remote_user__host__name',
                    'host_to_remote_user__remote_user__username')
                )
            }
            response.data = ret
            response.message = '初始化成功, 正在持续获取远程结果中...'
        except Exception as e:
            response.status = False
            response.error = e
        return response

    @staticmethod
    def put_result(request):
        response = BaseResponse()
        try:
            put_dict = QueryDict(request.body, encoding='utf-8')
            task_log_objs = models.TaskLogDetail.objects.filter(task_id=put_dict.get('task_id'))

            ret = {
                'putData': list(task_log_objs.values('id', 'status', 'result'))
            }
            response.data = ret
        except Exception as e:
            response.status = False
            response.error = '采集错误'
        return response




