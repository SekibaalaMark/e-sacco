from django.urls import path
from .views import *




urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
]
