import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_user_agency")]
    operations = [
        migrations.CreateModel(
            name="AgentVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=200)),
                ("date_of_birth", models.DateField()),
                ("nationality", models.CharField(default="Tanzanian", max_length=100)),
                ("address", models.TextField()),
                ("nida_number", models.CharField(max_length=50)),
                ("nida_document", models.FileField(upload_to="verifications/nida/")),
                ("birth_certificate", models.FileField(blank=True, null=True, upload_to="verifications/birth/")),
                ("passport_photo", models.ImageField(upload_to="verifications/passport/")),
                ("license_number", models.CharField(blank=True, max_length=100)),
                ("license_document", models.FileField(blank=True, null=True, upload_to="verifications/license/")),
                ("status", models.CharField(choices=[("pending", "Pending Review"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=20)),
                ("rejection_reason", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(null=True, blank=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="verification", to=settings.AUTH_USER_MODEL)),
            ],
        )
    ]
