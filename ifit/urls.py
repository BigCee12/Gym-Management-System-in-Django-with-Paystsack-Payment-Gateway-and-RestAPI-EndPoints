from django.urls import path, re_path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers




router = routers.DefaultRouter()
router.register("subscription", views.SubscriptionViewSet, basename="subscription"),
router.register("user-details", views.OutputUserViewSet, basename="user-details"),
router.register("plan_discount", views.PlanDiscountViewset, basename="plan_discount")


app_name = "ifit"
urlpatterns = [
    re_path(
        "activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        views.activate,
        name="activate",
    ),
    path("homepage/", views.homepage, name="homepage"),
    path("initiate_payment/", views.initiate_payment, name="initiate_payment"),
    path(
        "verify_payment/<str:paystack_payment_reference>/",
        views.verify_payment,
        name="verify_payment",
    ),
    path(
        "client_tag_search/<str:client_tag>",
        views.SearchUsingClientTagListApiView.as_view(),
    ),
    path("register/", views.RegisterApiView.as_view()),
    path("login/", views.Login.as_view()),
    path("register_subscription/", views.SubscriptionPurchaseApiView.as_view()),
    path("register_subscription_plan/", views.SubscriptionPlansApiView.as_view()),
    path("token-auth/", obtain_auth_token, name="api_token_auth"),
    path("default_route/", include(router.urls)),
]
