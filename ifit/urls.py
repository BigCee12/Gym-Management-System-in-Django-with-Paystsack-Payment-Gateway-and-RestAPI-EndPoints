from django.urls import path, re_path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers
from django.contrib.auth import views as auth_views


router = routers.DefaultRouter()
router.register("subscription", views.SubscriptionViewSet, basename="subscription"),
router.register("user-details", views.OutputUserViewSet, basename="user-details"),
router.register("plan_discount", views.PlanDiscountViewset, basename="plan_discount")


app_name = "ifit"
urlpatterns = [
    # re_path(
    #     "activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
    #     views.activate,
    #     name="activate",
    # ),
    path(
        "client_tag_search/<str:client_tag>",
        views.SearchUsingClientTagListApiView.as_view(),
    ),
    # path("register/", views.RegisterApiView.as_view()),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("register_subscription/", views.SubscriptionPurchaseApiView.as_view()),
    path("register_subscription_plan/", views.SubscriptionPlansApiView.as_view()),
    path("token-auth/", obtain_auth_token, name="api_token_auth"),
    path("default_route/", include(router.urls)),
    path(
        "initiate_payment/",
        views.PaystackInitiatePayment.as_view(),
        name="initiate_payment",
    ),
    path(
        "verify_payment_paystack/<str:paystack_payment_reference>/",
        views.VerifyPaymentAPI.as_view(),
        name="verify_payment_paystack",
    ),
    path("user_register/", views.UserRegistrationView.as_view()),
    path(
        "user_email_verification/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        views.UserActivationView.as_view(),
        name="activate",
    ),
]
