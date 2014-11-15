import json
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.utils import decorators
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.views.generic.detail import SingleObjectMixin

from django_unixusers import forms, models

import uuid

class ValidateEmailView(SingleObjectMixin, View):
    model = models.User
    slug_field = 'email_validation_code'

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        messages.add_message(self.request, messages.INFO,
                             "Got validation email for user '{}' at {}".format(user.username, user.email))
        if request.user.is_authenticated():
            if request.user != user:
                messages.add_message(self.request, messages.ERROR,
                                     'Attempting to validate email for one user while logged in as another is not allowed!')
                return HttpResponseRedirect(reverse('main'))
        user.email_validated = True
        user.email_validation_code = None
        user.save()

        return HttpResponseRedirect(reverse('profile'))


class RequestValidateEmailView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseBadRequest()
        if not request.user.email or request.user.email == '':
            return JsonResponse({'result': 'error', 'message': 'Invalid email'})
        base_url = "{}://{}".format(request.scheme, request.environ['HTTP_HOST'])
        request.user.email_validation_code = str(uuid.uuid4())
        request.user.save()
        email_body = render_to_string('django_unixusers/email/validate.html',
                                      {'user': request.user,
                                       'base_url': base_url})
        request.user.email_user("Validate your email", email_body)
        return JsonResponse({'result': 'ok'})


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
            messages.add_message(self.request, messages.WARNING,
                                 render_to_string('django_unixusers/messages/email_requires_validation.html'))
        context['forms'] = {
            'password_change': forms.PasswordChangeForm(),
        }
        return context
