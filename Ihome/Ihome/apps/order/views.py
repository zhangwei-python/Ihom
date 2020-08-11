from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django_redis import get_redis_connection
from house.models import *
from order.models import *
import datetime
from Ihome.utils.view import login_required


# Create your views here.

# 添加订单

class AddOrderView(View):
    def post(self, request):

        # get data
        data = json.loads(request.body.decode())
        # house_id = data.get('house_id')
        house_id = 6
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        # judge data
        if not all([house_id, start_date, end_date]):
            return JsonResponse({
                'errno': 400,
                'errmsg': '缺少必要参数'
            })
        # judge is loginning
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({
                'errno': 400,
                'errmsg': '请先登陆'
            })
        # judge owner house
        try:
            house = House.objects.get(id=house_id)
        except Exception as e:
            return JsonResponse({
                'errno': 400,
                'errmsg': '房间已下架'
            })
        if user.id == house.user_id:
            return JsonResponse({
                'errno': 400,
                'errmsg': '不可预定自己的房间'
            })
        # judge date
        order = Order.objects.get(house_id=house_id)
        bd = order.begin_date
        ed = order.end_date

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        if (bd <= start_date <= ed) or (bd <= end_date <= ed):
            return JsonResponse({
                'errno': 400,
                'errmsg': '房间已被预定'
            })
        count_day = (end_date - start_date).days
        house_prices = house.price,
        house_price= house_prices[0]
        count_price = house_price * count_day
        try:
            Order.objects.create(
                begin_date=start_date,
                end_date=end_date,
                days=count_day,
                house_price= house_price,
                amount= count_price,
                status= True,
                house_id=house_id,
                user_id=user.id
            )
        except Exception as e:
            print(e)
            return JsonResponse({
                "errno": "0",
                "errmsg": "数据写入失败",
            })

        order_id = Order.objects.get(user_id=user.id,house_id=house_id,begin_date=start_date).id
        return JsonResponse({
            "errno": "0",
            "errmsg": "下单成功",
            'data': order_id
        })

    def get(self, request):

        role = request.GET.get('role')
        if role == 'landlord':
            return JsonResponse({
                'code': '400',
                'errmsg': '无法获取房客信息',
            })
        user = request.user
        my_order = Order.objects.filter(user_id=user.id,)
        orders_list = []
        for orders in my_order:

            orders_list.append({
                "amount": orders.amount,
                "comment": orders.comment,
                "ctime": orders.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "days": orders.days,
                "end_date": orders.end_date.strftime("%Y-%m-%d"),
                "img_url": "http://oyucyko3w.bkt.clouddn.com/FhgvJiGF9Wfjse8ZhAXb_pYObECQ",
                "order_id": orders.id,
                "start_date": orders.begin_date.strftime("%Y-%m-%d"),
                "status": "COMPLETE",#orders.status,
                "title":  House.objects.get(id=orders.house_id).title
            })


        return JsonResponse({
            "data": {
                "orders": orders_list
            },
            "errmsg": "OK",
            "errno": "0"
        })














class MyHouseOrderView(View):
    def put(self,request):
        user = request.user
        data = json.loads(request.body.decode())
        action = data.get('action')
        order_id = data.get('order_id')     # //

        order_db = Order.objects.get(id=order_id) # //
        if action == 'accept':
            status = request.GET.get('status')
            if status == 1:
                return JsonResponse({
                    "errno": "0",
                    "errmsg": "取消接单"
                })
            elif status == 2:
                order_db.status = 2,
                order_db.save()
                return JsonResponse({
                    "errno": "0",
                    "errmsg": "操作成功"
                })
        elif action == 'reject':
            reason = request.GET.get('reason')
            order_db.comment = reason
            order_db.save()
            return JsonResponse({
                "errno": "0",
                "errmsg": "操作成功"
            })

class UserCommitView(View):
    def put(self,request):
        comment = request.GET.get('comment')

        order_id = comment.get('order_id')  # //
        oeder_commit = Order.objects.get(order_id=order_id)
        oeder_commit.comment =comment
        oeder_commit.save()
        return JsonResponse({
            "errno": "0",
            "errmsg": "评论成功"
        })

