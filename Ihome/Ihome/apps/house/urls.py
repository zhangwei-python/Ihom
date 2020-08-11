from django.urls import re_path

from house import views

urlpatterns=[
    re_path(r'^api/v1.0/areas$',views.ShowAreaView.as_view()),
    re_path(r"^api/v1.0/houses$",views.PublishHouseView.as_view()),
    re_path(r'^api/v1.0/user/houses$',views.MyHouseList.as_view()),
    re_path(r'^api/v1.0/houses/(?P<house_id>[1-9]\d+)/images$',views.Up_load.as_view()),
    re_path(r'^api/v1.0/houses/index$',views.House_recommend.as_view()),
    re_path(r'^api/v1.0/houses/(?P<house_id>[1-9]\d+)$',views.HouseIndexView.as_view())
]
