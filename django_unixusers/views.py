from django.contrib.auth.forms import UserCreationForm
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.utils import decorators
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django_unixusers import forms



class AccessControlMixin(object):

    @decorators.method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccessControlMixin, self).dispatch(*args, **kwargs)


class SignupView(TemplateView):
    template_name = 'django_unixusers/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.add_message(request, messages.ERROR,
                                 "You can't sign up while already logged in!")
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        context['form'] = forms.SignupForm()
        return context

    def _default_response(self, context):
        return render(self.request, self.template_name, context)

    def post(self, request, **kwargs):
        form = forms.SignupForm(request.POST)
        if request.POST['password1'] != request.POST['password2']:
            messages.add_message(request, messages.ERROR, 'Passwords did not match.')
            return self._default_response({'form': form})
        if not form.is_valid():
            return self._default_response({'form': form})
        new_user = form.save(commit=False)
        new_user.email_validated = False
        new_user.set_password(request.POST['password1'])
        new_user.save()
        messages.add_message(request, messages.INFO, "User created.  Please login.")
        return HttpResponseRedirect(reverse('profile'))



class FrontPageView(TemplateView):
    template_name = 'django_unixusers/main.html'


class ProfileView(AccessControlMixin, TemplateView):
    template_name = 'django_unixusers/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        if not self.request.user.email_validated:
            messages.add_message(self.request, messages.WARNING, 'Email still requires validation.')
        return context
