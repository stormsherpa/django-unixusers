
from django import forms

from django_unixusers import models


class SignupForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['username']

    username = forms.RegexField(label="Username", max_length=30,
                                regex=r'^[\w.@+-]+$')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")
