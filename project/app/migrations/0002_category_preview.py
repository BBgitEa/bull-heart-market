# Generated by Django 5.0 on 2023-12-11 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='preview',
            field=models.ImageField(default=1, upload_to='uploads/previews/'),
            preserve_default=False,
        ),
    ]
