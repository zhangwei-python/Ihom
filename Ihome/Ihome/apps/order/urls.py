from django.urls import re_path
from order.views import *

urlpatterns = [
    re_path(r'^api/v1.0/orders$',AddOrderView.as_view()),

    re_path(r'^api/v1.0/orders/[int:order_id]/status$',MyHouseOrderView.as_view()),

    re_path(r'^api/v1.0/orders/[int:order_id]/comment$', MyHouseOrderView.as_view()),


]