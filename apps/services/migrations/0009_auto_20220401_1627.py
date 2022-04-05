# Generated by Django 3.2.4 on 2022-04-01 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_alter_serviceprovider_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprovider',
            name='description',
            field=models.TextField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='image',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
    ]
