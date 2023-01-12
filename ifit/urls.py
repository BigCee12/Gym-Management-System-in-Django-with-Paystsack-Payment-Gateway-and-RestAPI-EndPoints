from django.urls import path,re_path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("user_register", user_register, name="user_register"),
    path("user_login/", user_login, name="user_login"),
    re_path(
        "activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        activate,
        name="activate",
    ),
]
