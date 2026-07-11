import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderItem, Product
from .serializers import (
    CheckoutSerializer,
    LoginSerializer,
    OrderSerializer,
    ProductSerializer,
    RegisterSerializer,
    UserSerializer,
)

FREE_DELIVERY_THRESHOLD = Decimal("999")
DELIVERY_FEE = Decimal("49")

CART_SESSION_KEY = "cart"  # {sku: quantity}


def index_view(request):
    """Serves the Bazarify single-page storefront."""
    return render(request, "index.html")


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
@api_view(["GET"])
def product_list(request):
    qs = Product.objects.all()

    category = request.query_params.get("category")
    if category and category != "all":
        qs = qs.filter(category=category)

    search = request.query_params.get("q")
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(subtitle__icontains=search)

    serializer = ProductSerializer(qs, many=True)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# Cart (stored server-side in the Django session)
# ---------------------------------------------------------------------------
def _get_cart_dict(request):
    return request.session.get(CART_SESSION_KEY, {})


def _save_cart_dict(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _cart_payload(request):
    cart = _get_cart_dict(request)
    skus = list(cart.keys())
    products = {p.sku: p for p in Product.objects.filter(sku__in=skus)}

    items = []
    subtotal = Decimal("0")
    total_quantity = 0

    for sku, qty in cart.items():
        product = products.get(sku)
        if not product:
            continue
        line_total = product.price * qty
        subtotal += line_total
        total_quantity += qty
        items.append(
            {
                "sku": product.sku,
                "name": product.name,
                "subtitle": product.subtitle,
                "icon": product.icon,
                "price": product.price,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    delivery_fee = Decimal("0") if subtotal == 0 or subtotal >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE

    return {
        "items": items,
        "total_quantity": total_quantity,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": subtotal + delivery_fee,
    }


@api_view(["GET"])
def cart_detail(request):
    return Response(_cart_payload(request))


@api_view(["POST"])
def cart_add(request):
    sku = request.data.get("sku")
    qty = int(request.data.get("qty", 1))
    if not sku:
        return Response({"detail": "sku is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(sku=sku)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    if product.stock == "sold":
        return Response({"detail": "Product is sold out."}, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_cart_dict(request)
    cart[sku] = cart.get(sku, 0) + qty
    _save_cart_dict(request, cart)
    return Response(_cart_payload(request))


@api_view(["POST"])
def cart_update(request):
    """Sets the absolute quantity for a sku. qty <= 0 removes it."""
    sku = request.data.get("sku")
    qty = int(request.data.get("qty", 0))
    if not sku:
        return Response({"detail": "sku is required."}, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_cart_dict(request)
    if qty <= 0:
        cart.pop(sku, None)
    else:
        cart[sku] = qty
    _save_cart_dict(request, cart)
    return Response(_cart_payload(request))


@api_view(["POST"])
def cart_remove(request):
    sku = request.data.get("sku")
    cart = _get_cart_dict(request)
    cart.pop(sku, None)
    _save_cart_dict(request, cart)
    return Response(_cart_payload(request))


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------
def _generate_order_number():
    stamp = str(int(timezone.now().timestamp()))[-6:]
    rand = random.randint(10, 99)
    return f"BZ-{stamp}{rand}"


@api_view(["POST"])
def checkout(request):
    cart_payload = _cart_payload(request)
    if not cart_payload["items"]:
        return Response({"detail": "Your basket is empty."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    order = Order.objects.create(
        order_number=_generate_order_number(),
        user=request.user if request.user.is_authenticated else None,
        full_name=data["full_name"],
        phone=data["phone"],
        address_line=data["address_line"],
        city=data["city"],
        pincode=data["pincode"],
        payment_method=data["payment_method"],
        subtotal=cart_payload["subtotal"],
        delivery_fee=cart_payload["delivery_fee"],
        total=cart_payload["total"],
    )

    for item in cart_payload["items"]:
        product = Product.objects.get(sku=item["sku"])
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=item["name"],
            unit_price=item["price"],
            quantity=item["quantity"],
        )

    # Clear the cart now that the order has been placed.
    _save_cart_dict(request, {})

    estimated_delivery = timezone.now() + timedelta(days=5)

    response_data = OrderSerializer(order).data
    response_data["estimated_delivery"] = estimated_delivery.strftime("%a, %d %b")
    return Response(response_data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    # Log the new user straight in so they don't have to submit the login
    # form again right after registering.
    login(request, user)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([AllowAny])
def current_user_view(request):
    if not request.user.is_authenticated:
        return Response({"authenticated": False})
    data = UserSerializer(request.user).data
    data["authenticated"] = True
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user)
    return Response(OrderSerializer(orders, many=True).data)
