from django.urls import re_path

from house import views

urlpatterns=[
    re_path(r'^api/v1.0/areas$',views.ShowAreaView.as_view()),
    re_path(r"^api/v1.0/houses$",views.PublishHouseView.as_view())
]