# Generated by Django 2.2.3 on 2019-07-11 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0017_auto_20190628_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='date_added',
            field=models.DateField(blank=True, verbose_name='Date of entry into Point Grey'),
        ),
        migrations.AlterField(
            model_name='student',
            name='first',
            field=models.CharField(max_length=30, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='student',
            name='homeroom',
            field=models.CharField(max_length=3, verbose_name='Homeroom'),
        ),
        migrations.AlterField(
            model_name='student',
            name='last',
            field=models.CharField(max_length=30, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='student',
            name='legal',
            field=models.CharField(max_length=30, verbose_name='Legal Name'),
        ),
        migrations.AlterField(
            model_name='student',
            name='sex',
            field=models.CharField(max_length=1, verbose_name='Sex'),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_num',
            field=models.PositiveIntegerField(verbose_name='Student Number'),
        ),
    ]
