
from django import forms
from django.contrib.auth import authenticate

from django_unixusers import models

class ProfileFormMixin(object):
    def __init__(self, *args, **kwargs):
        profile_form_name = forms.CharField(widget=forms.HiddenInput,
                                            initial=(self.__class__.__name__))
        super(ProfileFormMixin, self).__init__(*args, **kwargs)
        self.fields['profile_form_name'] = profile_form_name

class SignupForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['username', 'email']

    username = forms.RegexField(label="Username", max_length=30,
                                regex=r'^[\w.@+-]+$')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

class PasswordChangeForm(ProfileFormMixin, forms.Form):
    oldpassword = forms.CharField(label="Old Password", widget=forms.PasswordInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

    def is_valid(self):
        valid = super(PasswordChangeForm, self).is_valid()
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            self.add_error(None, 'Passwords did not match')
            return False
        return valid

    def is_oldpassword_valid(self, user):
        authuser = authenticate(username=user.username, password=self.cleaned_data['oldpassword'])
        if not authuser or not authuser.is_active:
            self.add_error(None, 'Invalid old password.')
            return False
        return authuser.is_active
