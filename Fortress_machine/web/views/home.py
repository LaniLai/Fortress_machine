# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from web.service import task
from repository import models


class IndexView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class HostsCMDView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'host_cmd.html')

    @method_decorator(login_required)
    def post(self, request):
        cls_obj = task.TaskAnalysis(request)
        response = task.TaskLogResult.fetch_result(cls_obj)
        return JsonResponse(response.__dict__)

    @method_decorator(login_required)
    def put(self, request):
        response = task.TaskLogResult.put_result(request)
        return JsonResponse(response.__dict__)


class HostsFileView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'host_file.html')

    @method_decorator(login_required)
    def post(self, request):
        cls_obj = task.TaskAnalysis(request)
        response = task.TaskLogResult.fetch_result(cls_obj)
        return JsonResponse(response.__dict__)

    @method_decorator(login_required)
    def put(self, request):
        response = task.TaskLogResult.put_result(request)
        return JsonResponse(response.__dict__)


class HostsLogView(View):
    @method_decorator(login_required)
    def get(self, request):
        log_data = models.TaskLogDetail.objects.all().order_by('date')
        return render(request, 'host_log.html', {'log_data': log_data})



