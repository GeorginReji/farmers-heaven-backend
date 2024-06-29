from django.contrib.auth import get_user_model
from django.db import models

from ..base.models import TimeStampedModel, upload_file


class DynamicSettings(TimeStampedModel):
    name = models.CharField(max_length=1024, blank=True, null=True)
    icon = models.CharField(max_length=1024, blank=True, null=True)
    value = models.CharField(max_length=1024, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_editable = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    is_deletable = models.BooleanField(default=True)

    class Meta:
        ordering = ['value']


class UploadedDocument(TimeStampedModel):
    name = models.CharField(max_length=1000, blank=True, null=True)
    image = models.FileField(upload_to=upload_file, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def image_path(self):
        return self.image.name


class Country(TimeStampedModel):
    name = models.CharField(max_length=1024, blank=True, null=True)
    country_code = models.CharField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)


class State(TimeStampedModel):
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=1024, blank=True, null=True)
    state_code = models.CharField(max_length=255, blank=True, null=True)
    is_territorial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']


class City(TimeStampedModel):
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=1024, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']


class ActivityLog(TimeStampedModel):
    record_by = models.ForeignKey(get_user_model(), blank=True, null=True, related_name='activity_action',
                                  on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(), blank=True, null=True, related_name='activity_user',
                             on_delete=models.PROTECT)
    change_fields = models.TextField(blank=True, null=True)
    new_data = models.TextField(blank=True, null=True)
    previous_data = models.TextField(blank=True, null=True)
    category = models.CharField(blank=True, null=True, max_length=1024)
    sub_category = models.CharField(blank=True, null=True, max_length=1024)
    action_on = models.CharField(blank=True, null=True, max_length=1024)
    db_table = models.CharField(blank=True, null=True, max_length=1024)
    action_type = models.CharField(blank=True, null=True, max_length=1024)
    is_active = models.BooleanField(default=False)


class ProductImages(TimeStampedModel):
    image = models.CharField(blank=True, null=True, max_length=1024)
    is_active = models.BooleanField(default=False)


class Products(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=1024)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(DynamicSettings, blank=True, null=True, on_delete=models.PROTECT)
    images = models.ManyToManyField(ProductImages, blank=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    stock = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
