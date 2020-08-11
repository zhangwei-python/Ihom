import re

import qiniu
from django.shortcuts import render

# Create your views here.


import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from qiniu import put_data

from Ihome.settings import dev
from house.models import House, HouseImage
from .models import User
from Ihome.utils.view import login_required



import random
import logging

from libs.yuntongxun.ccp_sms import CCP

logger = logging.getLogger('django')
from django.shortcuts import render
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from django import http
# Create your views here.
from django.views import View
import json
# from elasticsearch import logger
from django_redis import get_redis_connection
# from celery_tsks.sms.tasks import  ccp_send_sma_code


from libs.captcha.captcha import captcha
from libs.yuntongxun.ccp_sms import CCP


class ImageCodeView(View):
    # 图片类视图,验证码编号,上一次验证码编号
    def get(self, request):
        cur=request.GET.get('cur')
        if not cur:
            return JsonResponse({'errno':4103,'errmsg':'错误'})
        text, image = captcha.generate_captcha()
        print(text)
        redis_conn = get_redis_connection('verify_code')

        redis_conn.setex('img_%s' % cur, 300, text)

        return HttpResponse(
            image,
            content_type='image/jpg')

class SMSCodeView(View):
    #短信
    def post(self,reqeust):
        dict=json.loads(reqeust.body.decode())
        mobile=dict.get('mobile')
        id=dict.get('id')
        text=dict.get('text')
        if not all([mobile,id]):
            return http.JsonResponse({'errno': 400,
                                      'errmsg': '缺少必传参数'})

        redis_conn=get_redis_connection('verify_code')
        image_code_server=redis_conn.get('img_%s'%id)
        if image_code_server is None:
            return http.JsonResponse({'errno': 400,
                                  'errmsg': '图形验证码失效'})
        image_code_server=image_code_server.decode()
        if text!=image_code_server:
            return http.JsonResponse({'errno': 400,
                                      'errmsg': '输入图形验证码有误'})
        #  生成短信验证码：生成6位数验证码
            # 4、发送短信验证码
        conn = get_redis_connection('verify_code')
            # 判断60秒之内，是否发送过短信——判断标志信息是否存在
        flag = conn.get('flag_%s' % mobile)
        if flag:
            return JsonResponse({'errno': 400, 'errmsg': '请勿重复发送'})

        sms_code = '%06d' % random.randint(0, 999999)
        # logger.info(sms_code)
        print(sms_code)

        pl = conn.pipeline()
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('send_flag_%s' % mobile, 60, 1)
        pl.execute()
        print(sms_code)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # ccp_send_sms_code.delay(mobile,sms_code)
        return http.JsonResponse({'errno': 0,
                                  'errmsg': '发送短信成功'})




class RegisterView(View):
    """注册"""
    def post(self,request):
        dict=json.loads(request.body.decode())
        mobile=dict.get('mobile')
        phonecode=dict.get('phonecode')
        password=dict.get('password')
        # 校验(整体)
        if not all([mobile,phonecode,password]):
            return http.JsonResponse({'errno':400,
                                      'errmsg':'缺少必传参数'})
        if not re.match( r'^1[3-9]\d{9}$',mobile):
            return http.JsonResponse({'errno':400,
                                      'errmsg':'手机号格式错误'})

        # if not re.match(r'^[a-zA-Z0-9]{8,20}$',password):
        #     return http.JsonResponse({'code': 400,
        #                               'errmsg': '密码格式有误'})


        conn = get_redis_connection('verify_code')
        phonecode_server=conn.get('sms_%s' % mobile)
        print(phonecode_server)
        if not phonecode_server:
            return http.JsonResponse({'errno': 400,
                                     'errmsg': '短信验证码过期'})
        if phonecode != phonecode_server.decode():
            return http.JsonResponse({'errno': 400,
                                      'errmsg': '验证码有误'})
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'errno': 400,
                                      'errmsg': '密码格式有误'})
        try:
            user=User.objects.create_user(
                username=mobile,
                # phonecode=phonecode,
                mobile=mobile,
                password=password,
            )
        except Exception as e:
            print(e)
        login(request, user)

        # 4、构建响应
        response = http.JsonResponse({'errno': 0, 'errmsg': ' 注册成功'})
        response.set_cookie(
            'mobile',
            mobile,
            max_age=3600 * 24 * 14
        )
        return response




class Lgogin(View):
    '''登录功能'''
    def post(self,request):
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        if not all([mobile,password]):
            return JsonResponse({'errno':'4103','errmsg':'参数错误'})
        user = authenticate(username= mobile,
                            password = password)
        if user is None:
            return JsonResponse({'errno':'4105','errmsg':'用户身份错误'})
        login(request,user)
        response=JsonResponse({'errno':0,'errmsg':'成功'})
        response.set_cookie('mobile',mobile,max_age=3600*24*14)
        return response



    def delete(self,request):
        """退出登录"""
        logout(request)
        response=JsonResponse({
            "errno": "0",
            "errmsg": "已登出"
        })
        response.delete_cookie('mobile')
        return response


    @method_decorator(login_required)
    def get(self,request):
        '''判断是否登录'''
        user = request.user
        return JsonResponse({'errno':'0',
                             'errmsg':'已登录',
                             'data':{
                                 'name':user.username,
                                 'user_id':user.id
                             }
                             })





class UserInfo(View):
    def get(self, request):
        '''用户中心1.0'''
        user = request.user
        username = user.username
        user_db = User.objects.get(username=username)
        str_ava = str(user.avatar)

        return JsonResponse({
            'data': {
                'avatar_url': str_ava,
                'create_time': user.date_joined,
                'mobile': user.mobile,
                'name': user.username,
                'user_id': user_db.id},
            'errmsg': 'OK',
            'errno': 0,
        })


class Change_Username(View):
    '''修改用户名'''

    def put(self, request):
        data = json.loads(request.body.decode())
        newname = data.get('name')
        oldname = request.user.username

        if not newname:
            return JsonResponse({'errno': '4103', 'errmsg': '参数错误'})
        if not re.match(r'^1[3-9]\d{9}$', newname):
            return JsonResponse({'errno': '4103', 'errmsg': '参数错误'})
        user = User.objects.get(username=oldname)
        user.username = newname
        user.save()
        return JsonResponse({'errno': '0', 'errmsg': '修改成功'})


class Upload_picture(View):
    '''上传图片'''

    def post(self, request):
        data = request.FILES.get('avatar')
        q = qiniu.Auth(dev.QINIU_ACCESS_KEY, dev.QINIU_SECRET_KEY)
        token = q.upload_token(bucket=dev.QINIU_BUCKET_NAME)
        ret, res = put_data(token, None, data=data)
        ret.get('key')
        avatar_url = dev.QINIU_PREFIX_URL + dev.QINIU_CDN + '/' + ret['key']
        request.user.avatar=avatar_url
        request.user.save()

        return JsonResponse({
            'data': {
                'avatar_url': avatar_url,

            },
            'errno': '0',
            'errmsg': '上传头像成功'
        })


#
class CertificationView(View):
    """实名认证"""
    @method_decorator(login_required)
    def get(self,request):
        user=request.user
        return JsonResponse({"errno": "0",
            "errmsg": "认证信息保存成功",
            'data':{
                "real_name": user.real_name,
                    "id_card": user.id_card
            }

        })



    @method_decorator(login_required)
    def post(self,request):
        data=json.loads(request.body.decode())
        real_name=data.get('real_name')
        id_card=data.get('id_card')
        user=request.user

        if not all([real_name,id_card]):
            return JsonResponse({
                "errno": '4103',
                "errmsg": "参数错误"
            })

        try:
            user.real_name=real_name
            user.id_card=id_card
            user.save()
        except Exception as e:
            return JsonResponse({
                "errno": '4103',
                "errmsg": "数据错误"
            })

        return JsonResponse({
            "errno": "0",
            "errmsg": "认证信息保存成功"
        })



# class MYHouseView(View):
#     @method_decorator(login_required)
#     def get(self, request):
#         """展示房源信息"""
#         user = request.user
#
#         house_list = []
#
#         return JsonResponse({
#             "errmsg": "获取成功",
#             "errno": "0",
#             "data": house_list
#
#         })


