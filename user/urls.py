from django.urls import path
from user.views import (CreateUserView, ManageUserView)

from rest_framework_simplejwt.views import (
   TokenObtainPairView,
   TokenRefreshView,
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ManageUserView.as_view(), name="me"),
]

app_name = "user"
