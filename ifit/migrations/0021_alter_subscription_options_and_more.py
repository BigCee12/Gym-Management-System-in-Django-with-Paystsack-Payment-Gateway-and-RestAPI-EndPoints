# Generated by Django 4.0.6 on 2023-01-15 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifit', '0020_alter_subscription_plan_alter_subscription_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('plan',)},
        ),
        migrations.AlterField(
            model_name='subscription',
            name='paystack_payment_reference',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='price',
            field=models.CharField(max_length=100, null=True),
        ),
    ]