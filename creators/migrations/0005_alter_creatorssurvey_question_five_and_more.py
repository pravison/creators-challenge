# Generated by Django 5.1.4 on 2025-03-20 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creators', '0004_alter_accountmonetization_average_percentage_progress_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creatorssurvey',
            name='question_five',
            field=models.TextField(default='Which business industries or categories are you passionate to work with? list as many as you can'),
        ),
        migrations.AlterField(
            model_name='creatorssurvey',
            name='question_one_answer',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='creatorssurvey',
            name='question_three',
            field=models.TextField(default='Which video creation tools stack are you currently using?'),
        ),
    ]
