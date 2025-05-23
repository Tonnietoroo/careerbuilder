# Generated by Django 5.0.2 on 2025-03-11 21:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_cv_address_cv_email_cv_full_name_cv_phone_number_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="workexperience",
            name="cv",
        ),
        migrations.RemoveField(
            model_name="cv",
            name="address",
        ),
        migrations.RemoveField(
            model_name="cv",
            name="email",
        ),
        migrations.RemoveField(
            model_name="cv",
            name="full_name",
        ),
        migrations.RemoveField(
            model_name="cv",
            name="phone_number",
        ),
        migrations.RemoveField(
            model_name="cv",
            name="professional_summary",
        ),
        migrations.AlterField(
            model_name="cv",
            name="content",
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name="cv",
            name="generated_file",
            field=models.FileField(null=True, upload_to="generated_cvs/"),
        ),
        migrations.AlterField(
            model_name="cv",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.DeleteModel(
            name="Education",
        ),
        migrations.DeleteModel(
            name="WorkExperience",
        ),
    ]
