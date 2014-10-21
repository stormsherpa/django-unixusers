from django.contrib.auth.forms import UserCreationForm
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils import decorators
from django.shortcuts import render
from django.contrib import messages

from django_unixusers import forms


class AccessControlMixin(object):

    @decorators.method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccessControlMixin, self).dispatch(*args, **kwargs)


class SignupView(TemplateView):
    template_name = 'django_unixusers/signup.html'

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        context['form'] = forms.SignupForm()
        return context

    def post(self, request, **kwargs):
        form = forms.SignupForm(request.POST)
        if not form.is_valid:
            return render(request, self.template_name, {'form':form})
        messages.add_message(request, messages.INFO, "User creation form was valid.")
        return render(request, self.template_name, {'form':form})



class FrontPageView(TemplateView):
    template_name = 'django_unixusers/main.html'


class ProfileView(AccessControlMixin, TemplateView):
    template_name = 'django_unixusers/profile.html'