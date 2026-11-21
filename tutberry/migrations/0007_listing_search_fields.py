from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tutberry", "0006_user_profiles")]

    operations = [
        migrations.AddField(
            model_name="listingrecord",
            name="category",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="listingrecord",
            name="location",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddIndex(
            model_name="listingrecord",
            index=models.Index(
                fields=["status", "category", "location", "daily_rate"],
                name="listing_search_idx",
            ),
        ),
    ]
