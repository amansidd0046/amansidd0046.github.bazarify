from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.product_list, name="product-list"),
    path("cart/", views.cart_detail, name="cart-detail"),
    path("cart/add/", views.cart_add, name="cart-add"),
    path("cart/update/", views.cart_update, name="cart-update"),
    path("cart/remove/", views.cart_remove, name="cart-remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("auth/register/", views.register_view, name="auth-register"),
    path("auth/login/", views.login_view, name="auth-login"),
    path("auth/logout/", views.logout_view, name="auth-logout"),
    path("auth/me/", views.current_user_view, name="auth-me"),
    path("orders/mine/", views.my_orders_view, name="my-orders"),
]
