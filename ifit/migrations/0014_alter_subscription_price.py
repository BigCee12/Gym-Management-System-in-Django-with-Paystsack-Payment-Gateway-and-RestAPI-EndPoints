# Generated by Django 4.0.6 on 2023-01-04 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifit', '0013_alter_subscriptionplan_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='price',
            field=models.CharField(max_length=50, null=True),
        ),
    ]