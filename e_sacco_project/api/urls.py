from django.urls import path
from .views import *




urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('login/', LoginView.as_view(), name='login'), # Now protected!
    path('logout/', LogoutView.as_view(), name='logout'),

    path('promote-user/',PromoteUserView.as_view(),name='promote'),

    #Mobile money APIs
    path('save/',DepositView.as_view(),name='save'),
    path('callback/',PaymentCallbackView.as_view(),name='payment-callback')

]
