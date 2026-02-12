from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('ordinary', 'Ordinary'),
        ('treasurer', 'Treasurer'),
    ]
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15,unique=True)
    is_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=30,unique=True)
    role = models.CharField(max_length=15,choices=ROLE_CHOICES,default='ordinary')    

    def __str__(self):
        return self.username 
    


    


    


