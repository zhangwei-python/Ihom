from django.db.models import Q

from order.models import Order
from Ihome.utils.model import BaseModel
from django.db import models


class Area(BaseModel):
    """城区"""

    name = models.CharField(max_length=32, null=False, verbose_name="区域名字")

    class Meta:
        db_table = "tb_area"

class Facility(BaseModel):
    """设施信息"""

    name = models.CharField(max_length=32, null=False, verbose_name="设施名字")

    class Meta:
        db_table = "tb_facility"


class House(BaseModel):
    """房屋信息"""
    user = models.ForeignKey("users.User", related_name='houses', on_delete=models.CASCADE, verbose_name='房屋主人的用户编号')
    area = models.ForeignKey("Area", null=False, on_delete=models.CASCADE, verbose_name="归属地的区域编号")
    title = models.CharField(max_length=64, null=False, verbose_name="标题")
    price = models.IntegerField(default=0)  # 单价，单位：分
    address = models.CharField(max_length=512, default="")  # 地址
    room_count = models.IntegerField(default=1)  # 房间数目
    acreage = models.IntegerField(default=0)  # 房屋面积
    unit = models.CharField(max_length=32, default="")  # 房屋单元， 如几室几厅
    capacity = models.IntegerField(default=1)  # 房屋容纳的人数
    beds = models.CharField(max_length=64, default="")  # 房屋床铺的配置
    deposit = models.IntegerField(default=0)  # 房屋押金
    min_days = models.IntegerField(default=1)  # 最少入住天数
    max_days = models.IntegerField(default=0)  # 最多入住天数，0表示不限制
    order_count = models.IntegerField(default=0)  # 预订完成的该房屋的订单数
    index_image_url = models.CharField(max_length=256, default="")  # 房屋主图片的路径
    facility = models.ManyToManyField("Facility", verbose_name="和设施表之间多对多关系")

    class Meta:
        db_table = "tb_house"

class HouseImage(BaseModel):
    """
    房屋图片表
    """
    house = models.ForeignKey("House", on_delete=models.CASCADE)  # 房屋编号
    url = models.CharField(max_length=256, null=False)  # 图片的路径

    class Meta:
        db_table = "tb_house_image"