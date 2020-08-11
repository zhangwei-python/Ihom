from django.urls import re_path
from order.views import *

urlpatterns = [
    re_path(r'^api/v1.0/orders$',CustomOrderView.as_view()),

    re_path(r'^api/v1.0/orders/(?P<order_id>\d{1,5})/status$',LandlOrderView.as_view()),

    re_path(r'^api/v1.0/orders/(?P<order_id>\d{1,5})/comment$',CommitOrderView.as_view()),

]