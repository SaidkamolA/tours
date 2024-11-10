from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from cards.views import PaymentView
from .views import (
    VerifyEmailView, ResetPasswordRequestView,
    ResetPasswordConfirmView, UserViewSet, UserProfileView
)





urlpatterns = [
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('reset-password-request/', ResetPasswordRequestView.as_view(), name='reset-password-request'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('users/register/', UserViewSet.as_view({'post': 'create'}), name='user_register'),
    path('users/login/', TokenObtainPairView.as_view(), name='user_login'),
    path('users/', UserViewSet.as_view({'get': 'list'}), name='user_view'),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='user_detail'),
    path('pay/', PaymentView.as_view(), name='payment'),
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
]
