# Generated by Django 5.0.2 on 2025-03-19 10:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_remove_workexperience_cv_remove_cv_address_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coverletter",
            name="generated_file",
        ),
        migrations.AlterField(
            model_name="coverletter",
            name="company_address",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="coverletter",
            name="cv",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="documents.cv",
            ),
        ),
    ]
