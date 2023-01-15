from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from .models import *


class ViewAllSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    plan = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"


class OutputUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomClient
        fields = (
            "first_name",
            "last_name",
            "email",
            "sex",
            "phone_number",
            "client_tag",
        )
        


class SearchUsingClientTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomClient
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
        )


class RegisterUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password", "placeholder": "Your Password"},
    )
    phone_number = serializers.CharField(max_length=11)

    class Meta:
        model = CustomClient
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "sex",
            "phone_number",
        )
    def create(self, validated_data):
            user = CustomClient(
                email=validated_data['email'],
                password=validated_data['password'],
                
            )
            user.set_password(validated_data['password'])
            Token.objects.create(user=user)
            user.save()
            return user


class LoginUserSerializer(serializers.ModelSerializer):
    # read_only_fields = ["token"]
    class Meta:
        model = CustomClient
        fields = (
            "email",
            "password",
            
        )
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("user","plan","price","verified")


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("title","price","max_member","validity_days")


class PlanDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanDiscount
        fields = "__all__"
