# Generated by Django 4.0.6 on 2023-01-02 00:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifit', '0011_subscription_paystack_payment_reference_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('-reg_date',)},
        ),
    ]
