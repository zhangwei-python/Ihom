from django.contrib import admin
from django.urls import path,re_path

from users import views

urlpatterns = [
    re_path(r'^api/v1.0/imagecode$', views.ImageCodeView.as_view()),
    re_path(r'^api/v1.0/sms$',views.SMSCodeView.as_view()),
    re_path(r'^api/v1.0/users$', views.RegisterView.as_view()),
    re_path(r'^api/v1.0/session$',views.Lgogin.as_view()),
    re_path(r'^api/v1.0/user/$',views.UserInfo.as_view()),
    re_path(r"^api/v1.0/user/auth$",views.CertificationView.as_view()),
    # re_path(r'^api/v1.0/user/houses$',views.MYHouseView.as_view()),
    re_path(r'^api/v1.0/user/name$',views.Change_Username.as_view()),
    re_path(r'^api/v1.0/user/avatar$',views.Upload_picture.as_view()),
]
