from django.contrib import admin
from .models import *

# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_filter = ("email", "client_tag")
    list_display = ["first_name", "last_name", "client_tag"]


class TrainerAdmin(admin.ModelAdmin):
    list_display = ["fullname", "mobile", "is_active"]
    list_editable = ["is_active"]


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["user", "plan_validity"]


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "price",
        "verified",
    ]


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "price",
        "max_member",
    ]


class PlanDiscountAdmin(admin.ModelAdmin):
    list_display = [
        "plan",
        "duration",
        "discount_percent",
    ]


admin.site.register(CustomClient, CustomUserAdmin)
admin.site.register(Trainer, TrainerAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(PlanDiscount, PlanDiscountAdmin)
