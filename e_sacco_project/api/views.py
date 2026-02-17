from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser
from .permissions import *


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



from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Logged out successfully"}, status=status.HTTP_204_NO_CONTENT)
    







class PromoteUserView(APIView):
    permission_classes = [CanPromoteUsers]

    def post(self, request):
        serializer = PromoteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        role_name = serializer.validated_data['role']

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Remove all existing groups
        target_user.groups.clear()

        # Assign new role
        group = Group.objects.get(name=role_name)
        target_user.groups.add(group)

        if target_user.is_superuser:
            return Response(
                            {"error": "Cannot modify a superuser"},
                            status=status.HTTP_403_FORBIDDEN
                                        )
        

        return Response({
            "message": f"{target_user.username} promoted to {role_name}"
        }, status=status.HTTP_200_OK)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import DepositSerializer

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        savings = serializer.save()

        # Here is where you call MTN/Airtel API

        return Response({
            "message": "Payment initiated",
            "transaction_id": savings.transaction_id
        })





class PaymentCallbackView(APIView):

    authentication_classes = []  # Usually no JWT
    permission_classes = []      # Secured by provider secret

    def post(self, request):

        transaction_id = request.data.get("transaction_id")
        payment_status = request.data.get("status")

        try:
            savings = Savings.objects.get(transaction_id=transaction_id)
        except Savings.DoesNotExist:
            return Response({"error": "Invalid transaction"}, status=404)

        if payment_status == "SUCCESS":
            savings.status = "SUCCESS"
        else:
            savings.status = "FAILED"

        savings.save()

        return Response({"message": "Callback received"})
