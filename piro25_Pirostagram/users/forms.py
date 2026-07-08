from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


User = get_user_model()


class SignupForm(UserCreationForm):
    name = forms.CharField(
        max_length=30,
        label="이름",
    )

    email = forms.EmailField(
        required=False,
        label="이메일",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.name = self.cleaned_data["name"]
            profile.save()

        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "profile_image",
            "name",
            "bio",
        ]

        labels = {
            "profile_image": "프로필 사진",
            "name": "이름",
            "bio": "소개",
        }

        widgets = {
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-file-input",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "text-input",
                    "placeholder": "이름",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "text-input",
                    "placeholder": "자기소개",
                    "rows": 4,
                }
            ),
        }