import re

import qiniu
from django.shortcuts import render

# Create your views here.


import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from qiniu import put_data

from Ihome.settings import dev
from .models import User
from Ihome.utils.view import login_required


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
        return JsonResponse({'errno':0,'errmsg':'成功'})

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



class MYHouseView(View):
    @method_decorator(login_required)
    def get(self, request):
        """展示房源信息"""
        user = request.user

        house_list = []

        return JsonResponse({
            "errmsg": "获取成功",
            "errno": "0",
            "data": house_list

        })