from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Role

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Role.choices,
        label="Искана Роля",
        widget=forms.RadioSelect
    )
    first_name = forms.CharField(max_length=150, required=True, label="Име")
    last_name = forms.CharField(max_length=150, required=True, label="Фамилия")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'role',
                  'username')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = False
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        label="Идентификатор (Служебен Имейл или Факултетен Номер)",
        widget=forms.TextInput(attrs={'autofocus': True})
    )
