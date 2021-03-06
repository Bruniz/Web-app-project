# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-08 20:12
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('YAAS', '0019_auto_20161108_2011'),
    ]

    operations = [
        migrations.CreateModel(
            name='BidObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', models.DecimalField(decimal_places=2, default=1.0, help_text='The amount you want to raise the bid with', max_digits=8)),
            ],
        ),
        migrations.RemoveField(
            model_name='bid',
            name='bidder',
        ),
        migrations.DeleteModel(
            name='Bladibla',
        ),
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 11, 20, 12, 47, 642446, tzinfo=utc), help_text='Enter the date like: YYYY-MM-DD HH:MM'),
        ),
        migrations.DeleteModel(
            name='Bid',
        ),
        migrations.AddField(
            model_name='bidobject',
            name='auction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='YAAS.Auction'),
        ),
        migrations.AddField(
            model_name='bidobject',
            name='bidder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
