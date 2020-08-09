from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.conf import settings


class User(AbstractUser):

    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    avatar = models.ImageField(null=True, blank=True, verbose_name='用户头像')
    real_name = models.CharField(max_length=32, null=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=20, null=True, verbose_name="身份证号")

    class Meta:
        db_table = "tb_user"
