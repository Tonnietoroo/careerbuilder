# Generated by Django 5.0.2 on 2025-03-22 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interviews", "0010_alter_interviewprep_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="interviewprep",
            options={"ordering": ["-interview_date"]},
        ),
        migrations.AlterField(
            model_name="interviewprep",
            name="interview_date",
            field=models.DateField(),
        ),
    ]
