# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_unixusers', '0002_auto_20141024_0434'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_validation_code',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
