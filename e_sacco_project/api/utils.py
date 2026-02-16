from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def generate_verification_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token




def send_verification_email(user, request):
    # 1. Generate the UID and Token using your existing logic
    from .utils import generate_verification_token # Import here to avoid circular imports
    uid, token = generate_verification_token(user)

    # 2. Build the absolute URL
    # 'verify-email' must match the 'name' in your urls.py
    link = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    
    # We build the full URL (e.g., http://localhost:8000/api/verify/...)
    verify_url = f"{request.scheme}://{request.get_host()}{link}"

    # 3. Send the email
    subject = "Verify your email address"
    message = f"Hi {user.email}, please click the link below to verify your account:\n\n{verify_url}"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )