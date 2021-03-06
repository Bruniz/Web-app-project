# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-09 11:04
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('YAAS', '0024_auto_20161109_1102'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auction',
            options={'ordering': ['deadline']},
        ),
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 12, 11, 4, 0, 724591, tzinfo=utc), help_text='Enter the date like: YYYY-MM-DD HH:MM'),
        ),
    ]
