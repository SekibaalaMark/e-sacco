from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15,unique=True)
    is_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=30,unique=True)


    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_verified = True
        super().save(*args, **kwargs)   

    def __str__(self):
        return self.username 
    


    


    


