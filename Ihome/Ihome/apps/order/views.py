import json
from django.http import JsonResponse,HttpResponseRedirect
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

class CustomOrderView(View):
    def post(self, request):
        # get data
        data = json.loads(request.body.decode())
        house_id = data.get('house_id')
        #house_id = 6
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

        if ((bd <= start_date <= ed) or (bd <= end_date <= ed)) and():
            return JsonResponse({
                'errno': 400,
                'errmsg': '房间已被预定'
            })
        count_day = (end_date - start_date).days
        house_prices = house.price,
        house_price = house_prices[0]
        count_price = house_price * count_day
        try:
            Order.objects.create(
                begin_date=start_date,
                end_date=end_date,
                days=count_day,
                house_price=house_price,
                amount=count_price,
                status=0,
                house_id=house_id,
                user_id=user.id
            )
        except Exception as e:
            print(e)
            return JsonResponse({
                "errno": "0",
                "errmsg": "数据写入失败",
            })

        order_id = Order.objects.get(user_id=user.id, house_id=house_id, begin_date=start_date).id
        return JsonResponse({
            "errno": "0",
            "errmsg": "下单成功",
            'data': order_id
        })

    def get(self, request):
        role = request.GET.get('role')
        user = request.user
        if role == 'custom':
            my_order = Order.objects.filter(user_id=user.id, )
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
                    "status": orders.status,  # 前端order.html修改响应order.status（0-待接单/1-待评价/2-已完成/3-已拒单）
                    "title": House.objects.get(id=orders.house_id).title
                })
            return JsonResponse({
                "data": {
                    "orders": orders_list
                },
                "errmsg": "OK",
                "errno": "0"
            })

        elif role == 'landlord':
            my_house = House.objects.filter(user_id=user.id)
            orders_list = []
            for house in my_house:
                my_order = Order.objects.filter(house_id=house.id)
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
                        "status": orders.status,  # 前端order.html和lorder.html修改响应order.status（0-待接单/1-待评价/2-已完成/3-已拒单）
                        "title": House.objects.get(id=orders.house_id).title
                    })
            return JsonResponse({
                "data": {
                    "orders": orders_list
                },
                "errmsg": "OK",
                "errno": "0"
            })


class LandlOrderView(View):
    def put(self, request, order_id):
        user = request.user
        data = json.loads(request.body.decode())
        action = data.get('action')
        reason = data.get('reason')
        print(order_id)
        order = Order.objects.get(id=order_id)
        if action == 'accept':
            order.status = 1
            order.save()
            house = House.objects.get(id=order.house_id)
            h_room = house.room_count

            if h_room > 0:
                try:
                    house.room_count = h_room - 1
                    house.order_count = house.order_count + 1
                    house.save()
                except Exception as e:
                    print(e)
                    return JsonResponse({
                        "errno": "400",
                        "errmsg": "操作失败"
                    })
                return JsonResponse({
                    "errno": "0",
                    "errmsg": "操作成功"
                })
            elif h_room == 0:
                return JsonResponse({
                    "errno": "400",
                    "errmsg": "房源不足"
                })
        elif action == 'reject':
            try:
                order.status = 3
                order.comment = reason
                order.save()
            except Exception as e:
                print(e)
                return JsonResponse({
                    "errno": "400",
                    "errmsg": "操作失败"
                })
            return JsonResponse({
                "errno": "0",
                "errmsg": "操作成功"
            })


# 前端order.html修改响应order.status（0-待接单/1-待评价/2-已完成/3-已拒单）
class CommitOrderView(View):
    def put(self,request,order_id):
        data = json.loads(request.body.decode())
        comment = data.get('comment')
        if not comment.strip():
            return JsonResponse({
                {
                    "errno": "400",
                    "errmsg": "评论内容不能为空"
                }
            })
        oeder = Order.objects.get(id=order_id)
        try:
            oeder.comment = comment
            oeder.status = 2
            oeder.save()
        except Exception as e:
            print(e)
            return JsonResponse({
                "errno": "400",
                "errmsg": "评论失败"
            })
        return JsonResponse({
            "errno": "0",
            "errmsg": "评论成功"
        })
