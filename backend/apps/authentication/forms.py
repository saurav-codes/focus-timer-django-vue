from django import forms
from django.contrib.auth import get_user_model
from .models import User as UserModelType

User = get_user_model()

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self, commit=True) -> UserModelType:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
