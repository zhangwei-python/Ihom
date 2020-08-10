from django.http import JsonResponse
from django.utils.decorators import method_decorator

def login_required(func):
    def inner(request,*args,**kwargs):
        if request.user.is_authenticated:
            return func(request,*args,**kwargs)
        else:
            return JsonResponse({'errno': '4101', 'errmsg': '用户未登录'})
    return inner
