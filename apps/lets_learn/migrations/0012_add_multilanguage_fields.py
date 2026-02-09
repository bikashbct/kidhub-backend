from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lets_learn", "0011_categoryconfig_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoryconfig",
            name="name_ne",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="categoryconfig",
            name="name_hi",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
