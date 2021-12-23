from django.http import JsonResponse
from django.conf import settings

from apps.cart.cart import Cart
from .models import Coupon

def api_can_use(request):
    print(" ** api_can_use ** ")
    json_response = {}
    coupon_code = request.GET.get('coupon_code', '')
    print("coupon_code = ", coupon_code)
    cart=Cart(request)



    try:
        coupon = Coupon.objects.get(code=coupon_code)
        print("coupon = ", coupon.discount)
        if coupon.can_use():
            s_coupon = request.session.get(settings.COUPON_SESSION_ID)
            if not s_coupon:
                s_coupon = request.session[settings.COUPON_SESSION_ID] = {}
            s_coupon["code"] = coupon_code
            s_coupon["discount"] = coupon.discount
            request.session[settings.COUPON_SESSION_ID] = s_coupon
            cart.add_coupon(coupon_code,coupon.discount)
            print(request.session.get(settings.COUPON_SESSION_ID))
            json_response = {'amount': coupon.discount}
        else:
            json_response = {'amount': 0}
    except Exception as e:
        print(e)
        json_response = {'amount': 0}

    return JsonResponse(json_response)
