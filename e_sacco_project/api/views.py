from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser


class RegisterAPIView(APIView):
    
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered succesfully",
                    "user":{
                        "username": user.username,
                        "email": user.email,
                        "phone_number": user.phone_number
                    }
                },status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)









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




from django.contrib.auth import get_user_model


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