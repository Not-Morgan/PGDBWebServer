# Generated by Django 2.2.5 on 2019-10-04 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('principal_signature', models.ImageField(default='entry/uploads/no-img.jpg', upload_to='entry/uploads')),
            ],
        ),
    ]
