from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length = 8)
    confirm_password = serializers.CharField(write_only=True,min_length=8)


    class Meta:
        model = User 
        fields = ['username','email','phone_number','password','confirm_password']
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"Passwords":"Passwords do not match!!"})

        return attrs

    
    def create(self,validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        ordinary_group= Group.objects.get(name='Ordinary')  # even if the group doesn't exist no app crash
        user.groups.add(ordinary_group)
        return user




'''
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 1. Let the parent class handle the initial authentication (username/password)
        data = super().validate(attrs)

        # 2. At this point, self.user is available. Check the verification status.
        if not self.user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Your email address is not verified. Please check your inbox."}
            )

        return data
'''


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['groups'] = list(user.groups.values_list('name', flat=True))
        token['is_verified'] = user.is_verified
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)   # ✅ Authenticate first

        # Now self.user exists
        if not self.user.is_verified:
            raise serializers.ValidationError("Email not verified")

        # Add extra response data
        data['groups'] = list(self.user.groups.values_list('name', flat=True))
        data['is_verified'] = self.user.is_verified

        return data





from rest_framework_simplejwt.tokens import RefreshToken

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError("Invalid or expired token")



class PromoteUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=["Admin", "Treasurer"])




from rest_framework import serializers
from .models import Savings
import uuid

class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Savings
        fields = ['amount', 'provider']

    def create(self, validated_data):
        user = self.context['request'].user

        transaction_id = str(uuid.uuid4())

        savings = Savings.objects.create(
            user=user,
            amount=validated_data['amount'],
            provider=validated_data['provider'],
            transaction_id=transaction_id,
            status='PENDING'
        )

        return savings
