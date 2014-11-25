from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.hashers import identify_hasher, get_hasher

from django.conf import settings

from django_unixusers.hashers import BaseUnixPasswordHasher

class UnixGroup(models.Model):
    groupname = models.CharField(max_length=20, unique=True)
    gid = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.groupname


class UnixUser(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField(unique=True, blank=True, null=True)
    unix_groups = models.ManyToManyField(UnixGroup, blank=True)
    email_validated = models.BooleanField(default=True, blank=True)
    email_validation_code = models.CharField(max_length=50, blank=True, null=True)

    def get_password(self):
        hasher = identify_hasher(self.user.password)
        if isinstance(hasher, BaseUnixPasswordHasher):
            return self.user.password[len(hasher.algorithm):]
        else:
            return None

    def get_uid(self):
        if not self.uid:
            max_uid = self.__class__.objects.all().aggregate(models.Max('uid'))['uid__max']
            if max_uid:
                self.uid = max_uid + 1
            else:
                self.uid = settings.BASE_UNIX_UID
            self.save()
        return self.uid

    @classmethod
    def get_by_user(cls, user_obj):
        try:
            unixuser = cls.objects.get(user=user_obj)
        except cls.DoesNotExist:
            unixuser = cls(user=user_obj)
            unixuser.get_uid()
            unixuser.email_validated = False
            unixuser.save()
        return unixuser

    def __unicode__(self):
        return self.user.username


class AuthorizedKey(models.Model):
    user = models.ForeignKey(UnixUser, related_name='authorized_keys')
    name = models.CharField(max_length=50)
    sshkey = models.TextField(max_length=1024)
