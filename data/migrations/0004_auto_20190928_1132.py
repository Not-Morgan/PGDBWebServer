# Generated by Django 2.2.4 on 2019-09-28 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20190927_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='points',
            name='entered_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
