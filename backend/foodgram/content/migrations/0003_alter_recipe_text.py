# Generated by Django 3.2.18 on 2023-04-06 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(),
        ),
    ]