# Generated by Django 4.0.6 on 2022-11-02 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifit', '0009_plandiscount'),
    ]

    operations = [
        migrations.AddField(
            model_name='plandiscount',
            name='period',
            field=models.IntegerField(null=True),
        ),
    ]
