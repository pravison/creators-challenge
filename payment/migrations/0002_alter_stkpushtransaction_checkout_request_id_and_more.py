# Generated by Django 5.1.4 on 2025-02-16 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stkpushtransaction',
            name='checkout_request_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='stkpushtransaction',
            name='merchant_request_id',
            field=models.CharField(max_length=100),
        ),
    ]
