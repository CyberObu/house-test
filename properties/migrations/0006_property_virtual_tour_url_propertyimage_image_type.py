from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0005_nearbyplace"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="virtual_tour_url",
            field=models.URLField(blank=True, help_text="Matterport or other 3D virtual tour embed URL"),
        ),
        migrations.AddField(
            model_name="propertyimage",
            name="image_type",
            field=models.CharField(
                choices=[("photo", "Photo"), ("3d", "3D Render / 360°")],
                default="photo",
                max_length=10,
            ),
        ),
    ]
