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







