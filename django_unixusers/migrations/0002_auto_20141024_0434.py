# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('django_unixusers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizedKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('sshkey', models.TextField(max_length=1024)),
                ('user', models.ForeignKey(related_name=b'authorized_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='email_validated',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
