from django.conf.urls import url
from django.contrib import admin

from django_unixusers import models

# from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.contrib import messages
from django.utils.html import escape


class AuthorizedKeysInline(admin.StackedInline):
    model = models.AuthorizedKey


class UserAdmin(admin.ModelAdmin):
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password', 'uid', 'unix_groups')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('username', 'password', 'uid', )

    change_password_form = AdminPasswordChangeForm

    inlines = [AuthorizedKeysInline]

    def get_urls(self):
        return [
            url(r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password)),
        ] + super(UserAdmin, self).get_urls()

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.get_queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = 'Password changed successfully.'
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': 'Change password: %s' % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context())
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)


admin.site.register(models.User, UserAdmin)

admin.site.register(models.Group)
