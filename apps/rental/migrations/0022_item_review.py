# Generated by Django 3.2.4 on 2022-03-31 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0021_item_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='review',
            field=models.BooleanField(default=False),
        ),
    ]
