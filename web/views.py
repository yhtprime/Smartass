# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

# Create your views here.

# render(request,'form.html') 返回网页
from web.models import *

#启动定时器
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import datetime
import json,time
import requests
from web.models import *

#开启定时工作
try:
    # 实例化调度器
    weatherscheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    weatherscheduler.add_jobstore(DjangoJobStore(), "default")
    # @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='9', minute='30', second='10',id='task_time')
    # @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='0-23')
    @register_job(weatherscheduler, 'interval', hours=1)
    def job():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
            'Referer': 'http://www.weather.com.cn/weather1d/101070201.shtml',
        }
        url = 'http://d1.weather.com.cn/sk_2d/101070201.html?_=' + str(int(round(time.time() * 1000)))
        response = requests.get(url, headers=headers)
        text = response.content.decode('utf-8')
        print(text)
        # str 转 json
        res = json.loads(text[text.index("{"):])
        date = datetime.date.today()
        temp = res['temp']
        intro = res['WD'] + res['WS'] + " " + res['weather']
        pm = res['aqi_pm25']
        t = time.time()
        Weather.objects.create(date=date, intro=intro, temp=temp, pm=pm, time=t)
    register_events(weatherscheduler)
    weatherscheduler.start()
    # 控制考勤
    sched = BackgroundScheduler()
    #初始化（周数 日期 星期）
    def init():
        #获取日期
        now = datetime.datetime.now()
        #获取年
        year = now.year
        #获取月
        month = now.month
        #获取日
        day = now.day
        #获取周数
        #第一学期
        if month>=9 or month<=1:
            if(month<=1):
                startday = datetime.date(year-1, 9, 17).isocalendar()
            else:
                startday = datetime.date(year, 9, 17).isocalendar()
            nowday = datetime.date(year,month,day).isocalendar()
            #如果出现跨年的情况
            if nowday[0]-startday[0]>0:
                # 本年第一天
                this_year_start = datetime.datetime(now.year, 1, 1)
                # 去年第一天和最后一天
                last_year_end = this_year_start - datetime.timedelta(days=1)
                #防止日期算在今年的周里所以减去7
                lastyearweek = datetime.date(last_year_end.year-1,last_year_end.month,last_year_end.day-7).isocalendar()
                #计算去年总共过了多少周
                week = lastyearweek[1]-startday[1]
                #加上今年的周数
                week = week+nowday[1]
                Util.objects.filter(utilid=22).update(weekday=nowday[2],week=week,date=now.strftime("%Y-%m-%d"),year=year,month=month,day=day)
            else:
                week = nowday[1]-startday[1]
                Util.objects.filter(utilid=22).update(weekday=nowday[2], week=week, date=now.strftime("%Y-%m-%d"), year=year, month=month, day=day)
        #第二三学期
        elif month>=2 and month<9:
            startday = datetime.date(year, 2, 25).isocalendar()
            print(startday)
            nowday = datetime.date(year,month,day).isocalendar()
            print(nowday)
            week = nowday[1] - startday[1]
            Util.objects.filter(utilid=22).update(weekday=nowday[2], week=week, date=now.strftime("%Y-%m-%d"), year=year, month=month, day=day)
    #处理早上8点的课程请求
    def am8():
        #获取今天的数据
        u=Util.objects.get(utilid=22)
        #获取当天8点上课的课程
        classes = Class.objects.all()
        #把需要上课的课程存储到cn里
        cn = []
        checks = []
        #遍历进行筛选
        for c in classes:
            #把上课的节数给分割出来
            s,e = c.total.split('/')
            if str(u.weekday) in c.weekday and u.week in range(int(s),int(e)+1) and c.time==1:
                cn.append(c)
                #拿到课程后去check表里查找老师提交了的打卡信息并进行统计
                check = Check.objects.filter(classid=c,status=0).order_by('-checkid')
                #如果教师没有申请打卡则不动如果申请则关闭打卡通道
                if check:
                   check = check[0]
                   Check.objects.filter(classid=c,status=0).order_by('-checkid')[0].update(status=0)
                else:
                    pass
    def am9():
        # 先获取今天的数据
        u = Util.objects.get(utilid=22)
        # 先获取当天8点上课的课程
        classes = Class.objects.all()
        # 把需要上课的课程存储到cn里
        cn = []
        checks = []
        # 遍历进行筛选
        for c in classes:
            # 把上课的节数给分割出来
            s, e = c.total.split('/')
            if str(u.weekday) in c.weekday and u.week in range(int(s),int(e)+1) and c.time == 3:
                cn.append(c)
                # 拿到课程后去check表里查找老师提交了的打卡信息并进行统计
                check = Check.objects.filter(classid=c, status=0).order_by('-checkid')
                # 如果教师没有申请打卡则不动如果申请则关闭打卡通道
                if check:
                    check = check[0]
                    Check.objects.filter(classid=c, status=0).order_by('-checkid')[0].update(status=0)
                else:
                    pass
    def pm13():
        #先获取今天的数据
        u=Util.objects.get(utilid=22)
        #先获取当天8点上课的课程
        classes = Class.objects.all()
        #把需要上课的课程存储到cn里
        cn = []
        checks = []
        #遍历进行筛选
        for c in classes:
            #把上课的节数给分割出来
            s,e = c.total.split('/')
            if str(u.weekday) in c.weekday and u.week in range(int(s),int(e)+1) and c.time==5:
                cn.append(c)
                #拿到课程后去check表里查找老师提交了的打卡信息并进行统计
                check = Check.objects.filter(classid=c,status=0).order_by('-checkid')
                #如果教师没有申请打卡则不动如果申请则关闭打卡通道
                if check:
                   check = check[0]
                   Check.objects.filter(classid=c,status=0).order_by('-checkid')[0].update(status=0)
                else:
                    pass
    def pm15():
        # 先获取今天的数据
        u = Util.objects.get(utilid=22)
        # 先获取当天8点上课的课程
        classes = Class.objects.all()
        # 把需要上课的课程存储到cn里
        cn = []
        checks = []
        # 遍历进行筛选
        for c in classes:
            # 把上课的节数给分割出来
            s, e = c.total.split('/')
            if str(u.weekday) in c.weekday and u.week in range(int(s),int(e)+1) and c.time == 7:
                cn.append(c)
                # 拿到课程后去check表里查找老师提交了的打卡信息并进行统计
                check = Check.objects.filter(classid=c, status=0).order_by('-checkid')
                # 如果教师没有申请打卡则不动如果申请则关闭打卡通道
                if check:
                    check = check[0]
                    Check.objects.filter(classid=c, status=0).order_by('-checkid')[0].update(status=0)
                else:
                    pass
    def pm18():
        # 先获取今天的数据
        u = Util.objects.get(utilid=22)
        # 先获取当天8点上课的课程
        classes = Class.objects.all()
        # 把需要上课的课程存储到cn里
        cn = []
        checks = []
        # 遍历进行筛选
        for c in classes:
            # 把上课的节数给分割出来
            s, e = c.total.split('/')
            if str(u.weekday) in c.weekday and u.week in range(int(s),int(e)+1) and c.time == 9:
                cn.append(c)
                # 拿到课程后去check表里查找老师提交了的打卡信息并进行统计
                check = Check.objects.filter(classid=c, status=0).order_by('-checkid')
                # 如果教师没有申请打卡则不动如果申请则关闭打卡通道
                if check:
                    check = check[0]
                    Check.objects.filter(classid=c, status=0).order_by('-checkid')[0].update(status=0)
                else:
                    pass
    sched.add_job(init,'interval',minutes=30)
    sched.add_job(am8, 'cron', hour='8', minute='00', second='00')
    sched.add_job(am9, 'cron', hour='9', minute='30', second='00')
    sched.add_job(pm13, 'cron', hour='13', minute='20', second='00')
    sched.add_job(pm15, 'cron', hour='15', minute='00', second='00')
    sched.add_job(pm18, 'cron', hour='18', minute='00', second='00')
    # sched.add_job(my_job, 'cron', hour='20', minute='30', second='00')
    # 每天的20:30:00执行一次
    sched.start()
except Exception as e:
    print(e)
    # 有错误就停止定时器
    weatherscheduler.shutdown()
job()
init()
def login(request):
    md5 = hashlib.md5()
    md5.update(request.POST.get('passwd').encode("utf-8"))
    result = md5.hexdigest()
    print(result)
    admin = Admin.objects.filter(name=request.POST.get('name'),passwd=result)
    if admin:
        data = {
            "status": 1,
            "result": "登录成功",
            "authen": admin[0].adminid
        }
    else:
        data = {
            "status": 0,
            "result": "账号密码不正确"
        }

    return JsonResponse(data)