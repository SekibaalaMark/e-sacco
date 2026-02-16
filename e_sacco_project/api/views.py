from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser


from .utils import send_verification_email # Make sure this is imported

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            # 1. Save the user (they should have is_verified=False by default)
            user = serializer.save()

            # 2. Trigger the email sending logic
            try:
                send_verification_email(user, request)
                email_status = "Verification email sent."
            except Exception as e:
                # Log the error (optional) and notify the user
                email_status = "User registered, but verification email failed to send."

            return Response(
                {
                    "message": "User registered successfully",
                    "email_status": email_status,
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "phone_number": user.phone_number
                    }
                }, status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








'''
class VerifyEmailView(APIView):

    def get(self, request, uid, token):
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = CustomUser.objects.get(pk=user_id)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully"})
        
        return Response({"error": "Invalid or expired token"}, status=400)
'''



class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # 1. Decode the uidb64 back into a plain User ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # 2. Check if the user exists and the token is valid
        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        
        # 3. If something is wrong (token expired or tampered with)
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
    






from rest_framework.throttling import AnonRateThrottle
class ResendVerificationView(APIView):
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            
            # 1. Check if the user is already verified
            if user.is_verified:
                return Response({"message": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Trigger a new email with a fresh token
            send_verification_email(user, request)
            
            return Response({"message": "A new verification link has been sent to your email."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            # Security Tip: We return 200 even if the user doesn't exist 
            # to prevent "Email Enumeration" (hackers checking which emails are registered).
            return Response({"message": "If an account exists with this email, a link has been sent."}, status=status.HTTP_200_OK)
        



from rest_framework_simplejwt.views import TokenObtainPairView

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer