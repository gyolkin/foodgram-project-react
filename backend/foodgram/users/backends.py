from django.contrib.auth.backends import ModelBackend

from .models import User


class EmailBackend(ModelBackend):
    """Бэкенд для авторизации через email."""
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
