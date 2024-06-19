from random import randint

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(_('created'), auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(_('modified'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        abstract = True


def upload_file(instance, image):
    """
    Stores the attachment in a "per rb-gallery/module-type/yyyy/mm/dd" folder.
    :param instance, filename
    :returns ex: oct-gallery/User-profile/2016/03/30/filename
    """
    print(instance._meta, image)
    return 'seva-image/{model}/{image}'.format(
        model=instance._meta.model_name, image=str(randint(100000, 999999)) + "_" + image
    )
