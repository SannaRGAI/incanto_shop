from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

router = DefaultRouter()
router.register("profile", ProfileViewSet)

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('activate/<str:activation_code>/', activate),
    path('change_password/', ChangePasswordView.as_view()),
    path('forgot_password/', ForgotPasswordView.as_view()),
    path('forgot_password/<str:activation_code>/', NewPasswordView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('billing/top-up/', TopUpBillingView.as_view()),
    path('', include(router.urls)),
]
