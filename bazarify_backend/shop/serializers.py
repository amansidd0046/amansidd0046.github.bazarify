from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Order, OrderItem, Product

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["sku", "name", "subtitle", "category", "price", "stock", "icon"]


class OrderItemSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["sku", "product_name", "unit_price", "quantity", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_number",
            "full_name",
            "phone",
            "address_line",
            "city",
            "pincode",
            "payment_method",
            "subtotal",
            "delivery_fee",
            "total",
            "created_at",
            "items",
        ]


class CheckoutSerializer(serializers.Serializer):
    """Validates the shipping form submitted at checkout."""

    full_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20)
    address_line = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=12)
    payment_method = serializers.ChoiceField(choices=["cod", "upi", "card"])


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("That username is already taken.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

