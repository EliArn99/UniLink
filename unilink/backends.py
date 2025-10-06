from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class CustomAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username

        try:
            user = User.objects.get(
                Q(service_email__iexact=identifier) | Q(faculty_number__exact=identifier)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_approved:
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
