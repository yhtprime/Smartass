import hashlib
import json
import os
from base64 import encode

from django.core import serializers
from django.views import View

from django.http import HttpResponse,JsonResponse
import cv2 as cv
from PIL import Image
from smartass import settings, Utils
from smartass.settings import BASE_DIR
from web.models import *

#获取课程列表
class CourseList(View):
    def get(self,request):
        page = request.GET.get('page')
        major = request.GET.get('major')
        #条件搜索
        if major != None and page !=None:
            courses = Course.objects.raw('select c.*,m.mname from major m inner join course c  on m.majorid='+major+' and c.majorid = '+major)
            length = len(courses)
            temp = []
            for c in courses:
                temp.append(
                    {'courseid': c.courseid, 'name': c.name,  'mname': c.mname,'info': c.intro, 'major': c.majorid.majorid, 'status': c.status})
            data = {
                "status": 1,
                "result": "查询成功",
                "data": temp[abs(int(page) - 1) * 10:abs(int(page) - 1) * 10 + 10],
                "page": abs(int(page)),
                "len": length
            }
            return JsonResponse(data)
        #带专业查询
        elif page == None and major != None:
            courses = Course.objects.raw('select c.*,m.mname from major m inner join course c  on m.majorid='+major+' and c.majorid = '+major)
            length = len(courses)
            temp = []
            for c in courses:
                temp.append(
                    {'courseid': c.courseid, 'name': c.name, 'mname': c.mname, 'info': c.intro,
                     'major': c.majorid.majorid, 'status': c.status})
            data = {
                "status": 1,
                "result": "查询成功",
                "data": temp[0:10],
                "page": 1,
                "len": length
            }
            return JsonResponse(data)
       #普通搜索
        courses = Course.objects.raw('select c.*,m.mname from major m inner join course c  on c.majorid= m.majorid')
        length = len(courses)
        temp = []
        for c in courses:
            temp.append(
                {'courseid': c.courseid, 'name': c.name, 'mname': c.mname, 'info': c.intro,
                 'major': c.majorid.majorid, 'status': c.status})
        data = {
            "status": 1,
            "result": "查询成功",
            "data": temp[0:10],
            "page": 1,
            "len": length
        }
        return JsonResponse(data)
#添加课程
class AddCourse(View):
    def post(self,request):
        name = request.POST.get('name')
        info = request.POST.get('info')
        major = request.POST.get('major')
        major = Major.objects.get(majorid=major)
        # 插入数据
        if Course.objects.create(name=name, majorid=major,status=1,intro=info):
            data = {
                "status": 1,
                "result": "添加成功",
            }
            return JsonResponse(data)
        else:
            data = {
                "status": 0,
                "result": "添加失败",
            }
            return JsonResponse(data)


#修改课程
class ChangeCourse(View):
    def post(self,request):
        name = request.POST.get('name')
        info = request.POST.get('info')
        major = request.POST.get('major')
        cid = request.POST.get('cid')
        if Course.objects.filter(courseid=cid).update(name=name,intro=info,majorid=major):
            data = {
                "status": 1,
                "result": "修改成功",
            }
            return JsonResponse(data)
        else:
            data = {
                "status": 0,
                "result": "修改失败",
            }
            return JsonResponse(data)


#修改课程状态
class ChangeCStatus(View):
    def post(self,request):
        courseid = request.POST.get('courseid')
        status = request.POST.get('status')
        if Course.objects.filter(courseid=courseid).update(status = status):
            data = {
                "status": 1,
                "result": "修改成功",
            }
            return JsonResponse(data)
        else:
            data = {
                "status": 0,
                "result": "修改失败",
            }
            return JsonResponse(data)