# Generated by Django 5.1.4 on 2025-03-20 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creators', '0006_creatorssurvey_question_13_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creatorssurvey',
            name='question_13_answer',
            field=models.CharField(blank=True, choices=[('yes', 'yes'), ('no', 'no')], max_length=200, null=True),
        ),
    ]
