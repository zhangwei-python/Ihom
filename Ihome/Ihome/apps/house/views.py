import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator

from django.views import View

from Ihome.utils.view import login_required
from house.models import Area, House


class ShowAreaView(View):
    """显示地区"""
    def get(self,request):
        areas=Area.objects.all()
        #print(areas)
        area_list=[]
        for area in areas:
            area_list.append({
                'aid':area.id,
                'aname':area.name
            })


        return JsonResponse(
            {
                "errmsg": "获取成功",
                "errno": "0",
                "data":area_list
            }
        )


class PublishHouseView(View):
    "发布房源"

    def post(self,request):
        user=request.user
        #获取参数
        data=json.loads(request.body.decode())
        title=data.get('title')
        price=data.get('price')
        area_id=data.get('area_id')
        address=data.get('address')
        room_count=data.get('room_count')
        acreage=data.get('acreage')
        unit=data.get('unit')
        capacity=data.get('capacity')
        beds=data.get('beds')
        deposit=data.get('deposit')
        min_days=data.get('min_days')
        max_days=data.get('max_days')
        facility=data.get('facility')
        print(facility)
        #校验参数
        if not all([title,price,area_id,address,room_count,
                    acreage,unit,capacity,beds,
                    deposit,min_days,max_days,facility]):
            return JsonResponse({
                "errno": "400",
                "errmsg": "缺少参数",
            })

        try:
            house=House.objects.create(
                title=title,
                price=price,
                address=address,
                room_count=room_count,
                acreage=acreage,
                unit=unit,
                capacity=capacity,
                beds=beds,
                deposit=deposit,
                max_days=max_days,
                min_days=min_days,


                area_id=area_id,
                user_id=user.id
            )
            for f in facility:
                house.facility.add(f)


        except Exception as e:
            print(e)
            return JsonResponse({
                "errno": "400",
                "errmsg": "创建房源失败",
            })

        return JsonResponse({
            "errno": "0",
            "errmsg": "发布成功",
            "data": {
                "house_id": house.id}
        })











