# Generated by Django 2.1.1 on 2018-12-04 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0010_auto_20181107_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pointcodes',
            old_name='type',
            new_name='catagory',
        ),
    ]