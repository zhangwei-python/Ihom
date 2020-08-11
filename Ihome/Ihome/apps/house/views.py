import json

import qiniu
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator

from django.views import View
from qiniu import put_data

from Ihome.settings import dev
from Ihome.utils.view import login_required
from house.models import Area, House, HouseImage
from django.db.models import Q

from order.models import Order


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
    def get(self,request):
        "房屋搜索"
        aid=request.GET.get('aid')
        sd=request.GET.get('sd')
        ed=request.GET.get('ed')
        sk=request.GET.get('sk')

        if sk=='new':
            if not all([aid,sd,ed]):
                houses=House.objects.filter(Q(area_id=aid)|Q(update_time__lt=sd)).order_by('-create_time')
            else:
                houses=House.objects.filter(area_id=aid,update_time__lt=sd).order_by('-create_time')
        elif sk=="booking":
            if not all([aid, sd, ed]):
                houses = House.objects.filter(Q(area_id=aid) | Q(update_time__lt=sd)).order_by('-order_count')
            else:
                houses = House.objects.filter(area_id=aid, update_time__lt=sd).order_by('-order_count')
        elif sk=="price-inc":

                if not all([aid, sd, ed]):
                    houses = House.objects.filter(Q(area_id=aid) | Q(update_time__lt=sd)).order_by('price')
                else:
                    houses = House.objects.filter(area_id=aid, update_time__lt=sd).order_by('price')

        elif sk=='price-des':
            if not all([aid, sd, ed]):
                houses = House.objects.filter(Q(aeea_id=aid) | Q(update_time__lt=sd)).order_by('-price')
            else:
                houses = House.objects.filter(area_id=aid, update_time__lt=sd).order_by('-price')
        house_list=[]
        for house in houses:
            house_list.append(
                {
                    "address": house.address,
                    "area_name": house.area.name,
                    "ctime":house.create_time,
                    "house_id": house.id,
                    "img_url": str(house.index_image_url),
                    "order_count": house.order_count,
                    "price": house.price,
                    "room_count": house.room_count,
                    "title": house.title,
                    "user_avatar": str(house.user.avatar)
                }
            )
        return JsonResponse({
            "data": {
                "houses": house_list
            ,
                "total_page": 2
            },
            "errmsg": "请求成功",
            "errno": "0"
        })



    def post(self,request):
        "发布房源"
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



class MyHouseList(View):
    """我的房屋列表"""
    @method_decorator(login_required)
    def get(self,request):
        user=request.user
        #获取房源
        houses=House.objects.filter(user_id=user.id)

        house_list=[]
        for house in houses:
            house_list.append(
                {"address": house.address,
                "area_name": house.area.name,
                "ctime": house.create_time,
                "house_id": house.id,
                "img_url": "http://oyucyko3w.bkt.clouddn.com/FhxrJOpjswkGN2bUgufuXPdXcV6w",
                "order_count": house.order_count,
                "price": house.price,
                "room_count": house.room_count,
                "title": house.title,
                "user_avatar": str(house.user.avatar)}
            )

        return JsonResponse(
            {
                "data": {
                    "houses": house_list

                },
                "errmsg": "ok",
                "errno": "0"
            }
        )





class Up_load(View):
    @method_decorator(login_required)
    def post(self, request, house_id):
        data = request.FILES.get('house_image')
        q = qiniu.Auth(dev.QINIU_ACCESS_KEY, dev.QINIU_SECRET_KEY)
        token = q.upload_token(bucket=dev.QINIU_BUCKET_NAME)
        ret, res = put_data(token, None, data=data)
        ret.get('key')
        house_url = dev.QINIU_PREFIX_URL + dev.QINIU_CDN + '/' + ret['key']
        house = House.objects.get(id=house_id)
        house.index_image_url = house_url
        house.save()
        house_img = HouseImage.objects.create(house_id=house.id,
                                              url=house_url)


        return JsonResponse({'data': {'url': house_url},
                             'errno': '0',
                             'errmsg': '图片上传成功'})








class House_recommend(View):
    """房屋推荐"""
    def get(self, request):
        # data = json.loads(request.body.decode())
        houses = House.objects.all().order_by('-create_time')[0:5]
        print(houses)
        data_list = []
        for i in houses:
            data_list.append({'house_id': i.id, 'img_url': i.index_image_url, 'title': i.title})

        return JsonResponse({'data': data_list,
                             'errmsg': 'ok',
                             'errno': '0'})



