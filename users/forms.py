from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


User = get_user_model()


import logging
logger = logging.getLogger('users')

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        help_text= _("Enter your email account address. We will send you a link to reset your password.")
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        logger.debug(f'Checking email: {email}')
        if not User.objects.filter(email=email).exists():
            logger.debug(f'Email {email} is not registered.')
            raise forms.ValidationError("This email address is not registered.")
        logger.debug(f'Email {email} is registered.')
        return email





class CustomUserCreationForm(UserCreationForm):
    
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class LoginForm(forms.Form):

    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)
