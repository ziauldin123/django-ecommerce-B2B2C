# Generated by Django 3.2.4 on 2022-03-31 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_serviceprovider'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
    ]