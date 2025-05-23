# Generated by Django 5.0.2 on 2025-03-17 21:23

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interviews", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="interviewprep",
            old_name="position",
            new_name="job_title",
        ),
        migrations.RemoveField(
            model_name="interviewprep",
            name="industry",
        ),
        migrations.AddField(
            model_name="interviewprep",
            name="questions",
            field=models.ManyToManyField(to="interviews.interviewquestion"),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="interviewprep",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="interviewquestion",
            name="industry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="interviews.industry",
            ),
        ),
        migrations.AlterField(
            model_name="interviewquestion",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("general", "General"),
                    ("technical", "Technical"),
                    ("behavioral", "Behavioral"),
                ],
                max_length=20,
            ),
        ),
    ]
