# Generated by Django 5.1.4 on 2025-04-09 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0004_alter_contentcreationjob_job_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='budget',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='challenge_reward',
            field=models.IntegerField(default=0, help_text='whats the reward for the challenge'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='pay_per_1000_views',
            field=models.IntegerField(default=0, help_text='how much are you paying for 100 views'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='target_winners',
            field=models.IntegerField(default=5, help_text='how many winners do you want for this challenge'),
        ),
    ]
