from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models

from django.conf import settings

import crypt
import time


class Group(models.Model):
    groupname = models.CharField(max_length=20, unique=True)
    gid = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.groupname


class User(AbstractUser):
    uid = models.IntegerField(unique=True, blank=True, null=True)
    unix_groups = models.ManyToManyField(Group, blank=True)

    def set_password(self, raw_password):
        salt = crypt.crypt(str(time.time()), '$5$')[30:]
        seed = "$5${}".format(salt)
        self.password = crypt.crypt(raw_password, seed)

    def check_password(self, raw_password):
        checkpass = crypt.crypt(raw_password, self.password)
        return checkpass == self.password

    def get_uid(self):
        if not self.uid:
            max_uid = User.objects.all().aggregate(models.Max('uid'))['uid__max']
            if max_uid:
                self.uid = max_uid + 1
            else:
                self.uid = settings.BASE_UNIX_UID
            self.save()
        return self.uid
