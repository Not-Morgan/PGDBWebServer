# Generated by Django 2.2.5 on 2019-09-28 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20190910_0915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['last', 'first']},
        ),
        migrations.AddField(
            model_name='points',
            name='entered_by',
            field=models.CharField(blank=True, default='Administration', max_length=15),
        ),
    ]
