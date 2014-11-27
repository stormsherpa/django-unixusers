
from django.contrib import admin

from django_unixusers import models


class AuthorizedKeysInline(admin.StackedInline):
    model = models.AuthorizedKey


class UnixUserAdmin(admin.ModelAdmin):
    model = models.UnixUser
    inlines = [ AuthorizedKeysInline ]


admin.site.register(models.UnixUser, UnixUserAdmin)

admin.site.register(models.UnixGroup)
