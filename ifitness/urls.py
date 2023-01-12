"""ifitness URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from ifit import views
from rest_framework.authtoken.views import obtain_auth_token

# import rest_framework

router = routers.DefaultRouter()
router.register("subscription", views.SubscriptionViewSet, basename="subscription"),
router.register("user-details", views.OutputUserViewSet, basename="user-details"),
router.register("plan_discount", views.PlanDiscountViewset, basename="plan_discount")
app_name = "ifit"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("homepage/", views.homepage, name="home"),
    path("payment/", views.initiate_payment, name="initiate_payment"),
    path(
        "verify_payment/<str:paystack_payment_reference>/",
        views.verify_payment,
        name="verify_payment",
    ),
    # path("", include("ifit.urls")),
    path("", include(router.urls)),
    path(
        "client_tag_search/<str:client_tag>",
        views.SearchUsingClientTagListApiView.as_view(),
    ),
    path("register/", views.RegisterApiView.as_view()),
    path("login/", views.Login.as_view()),
    path("register_subscription/", views.SubscriptionPurchaseApiView.as_view()),
    path("register_subscription_plan/", views.SubscriptionPlansApiView.as_view()),
    path("token-auth/", obtain_auth_token, name="api_token_auth"),
]
