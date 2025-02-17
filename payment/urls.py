from django.urls import path
from .views import stk_push, b2c_pay, stk_push_callback, b2c_callback

urlpatterns = [
    path("stk-push/", stk_push, name="stk_push"),
    path("b2c-pay/", b2c_pay, name="b2c_pay"),
    path("stk-callback/", stk_push_callback, name="stk_callback"),
    path("b2c-callback/", b2c_callback, name="b2c_callback"),
]