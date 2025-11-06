from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "country",
            "phone",
            "avatar",
        )


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "email",
            "country",
            "phone",
            "avatar",
        )
