from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from .models import Profile


class ProfileCreateForm(forms.ModelForm):

    birthdate = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "text", "placeholder": "YYYY-MM-DD", "class": "datepicker"}
        ),
    )
    sex = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=Profile.Sex.choices,
        )

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "sex", "birthdate")
