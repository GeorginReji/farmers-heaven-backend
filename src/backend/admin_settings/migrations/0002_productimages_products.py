# Generated by Django 4.2.4 on 2024-06-29 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("admin_settings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductImages",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified"),
                ),
                ("image", models.CharField(blank=True, max_length=1024, null=True)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Products",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified"),
                ),
                ("name", models.CharField(blank=True, max_length=1024, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("price", models.PositiveIntegerField(blank=True, null=True)),
                ("stock", models.PositiveIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admin_settings.dynamicsettings",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "images",
                    models.ManyToManyField(
                        blank=True, to="admin_settings.productimages"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]