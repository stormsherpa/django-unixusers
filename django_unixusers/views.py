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
    model = models.UnixUser
    slug_field = 'email_validation_code'

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        messages.add_message(self.request, messages.INFO,
                             "Got validation email for user '{}' at {}".format(user.user.username, user.user.email))
        if request.user.is_authenticated():
            if request.user != user.user:
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
        unixuser = models.UnixUser.get_by_user(request.user)
        unixuser.email_validation_code = str(uuid.uuid4())
        unixuser.save()
        email_body = render_to_string('django_unixusers/email/validate.html',
                                      {'user': unixuser,
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
        unixuser = models.UnixUser.get_by_user(self.request.user)
        if not unixuser.email_validated:
            messages.add_message(self.request, messages.WARNING,
                                 render_to_string('django_unixusers/messages/email_requires_validation.html'))
        context['forms'] = {
            'password_change': forms.PasswordChangeForm(),
        }
        return context

    def post(self, request):
        form_name = request.POST.get('profile_form_name')
        if form_name == 'PasswordChangeForm':
            passform = forms.PasswordChangeForm(request.POST)
            if passform.is_valid() and passform.is_oldpassword_valid(request.user):
                request.user.set_password(passform.cleaned_data['password1'])
                request.user.save()
                messages.add_message(request, messages.SUCCESS, 'Password Changed.')
            else:
                for e in passform.errors.keys():
                    for err in passform.errors[e]:
                        messages.add_message(request, messages.ERROR, err)

        else:
            messages.add_message(request, messages.WARNING,
                                 "Nothing done! {}".format(form_name))
        return HttpResponseRedirect(reverse('profile'))
