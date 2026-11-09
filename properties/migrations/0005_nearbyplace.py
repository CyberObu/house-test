from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0004_alter_property_area"),
    ]

    operations = [
        migrations.CreateModel(
            name="NearbyPlace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("place_type", models.CharField(
                    choices=[
                        ("hospital", "Hospital"),
                        ("clinic", "Clinic / Health Centre"),
                        ("school", "School"),
                        ("university", "University / College"),
                        ("restaurant", "Restaurant / Café"),
                        ("supermarket", "Supermarket / Market"),
                        ("bank", "Bank / ATM"),
                        ("pharmacy", "Pharmacy"),
                        ("park", "Park / Garden"),
                        ("gym", "Gym / Sports Centre"),
                        ("mosque", "Mosque"),
                        ("church", "Church"),
                        ("bus_stop", "Bus Stop"),
                        ("airport", "Airport"),
                        ("mall", "Shopping Mall"),
                        ("other", "Other"),
                    ],
                    default="other",
                    max_length=20,
                )),
                ("distance", models.CharField(blank=True, help_text="e.g. 500m, 2km", max_length=50)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("property", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="nearby_places",
                    to="properties.property",
                )),
            ],
            options={"ordering": ["order", "id"]},
        ),
    ]
