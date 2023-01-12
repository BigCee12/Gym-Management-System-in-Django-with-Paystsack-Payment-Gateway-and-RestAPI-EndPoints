# Generated by Django 3.0.8 on 2022-07-15 15:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ifit', '0005_auto_20220713_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('price', models.IntegerField()),
                ('max_member', models.IntegerField(null=True)),
                ('highlight_status', models.BooleanField(default=False, null=True)),
                ('validity_days', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='title',
        ),
        migrations.AddField(
            model_name='subscription',
            name='reg_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ifit.SubscriptionPlan'),
        ),
    ]