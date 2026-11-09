from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("properties", "0006_property_virtual_tour_url_propertyimage_image_type")]
    operations = [
        migrations.AddField(
            model_name="property",
            name="approval_status",
            field=models.CharField(
                choices=[("pending", "Pending Review"), ("approved", "Approved"), ("rejected", "Rejected")],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="property",
            name="rejection_reason",
            field=models.TextField(blank=True),
        ),
    ]
