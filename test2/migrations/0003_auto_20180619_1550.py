# Generated by Django 2.0.5 on 2018-06-19 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0002_awards_certificates_pointcodes_points_scholar'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='legal',
            field=models.CharField(default='default', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grade',
            name='anecdote',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]