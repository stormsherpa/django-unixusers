
from django.core.management.base import BaseCommand, CommandError

from django_unixusers import models

import json


class Command(BaseCommand):
    help = 'Output json used by salt pillars'

    def handle(self, *args, **options):
        obj_out = {'users': dict(), 'groups': dict()}
        for user in models.User.objects.all():
            user_groups = [x.groupname for x in user.unix_groups.all()]
            u = {'username': user.username,
                 'password': user.password,
                 'is_staff': user.is_staff,
                 'is_superuser': user.is_superuser,
                 'groups': user_groups,
                 'uid': user.get_uid(),
                 }
            obj_out['users'][user.username] = u
        for group in models.Group.objects.all():
            g = {'groupname': group.groupname,
                 'gid': group.gid,
                 }
            obj_out['groups'][group.groupname] = g
        print json.dumps({'django_unixusers': obj_out}, indent=2)