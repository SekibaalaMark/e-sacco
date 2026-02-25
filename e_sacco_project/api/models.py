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



from django.conf import settings

class Savings(models.Model):

    PROVIDER_CHOICES = [
        ('MTN', 'MTN'),
        ('AIRTEL', 'Airtel'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

    


    


    


