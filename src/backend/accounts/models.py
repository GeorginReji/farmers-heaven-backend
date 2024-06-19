# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, \
    PermissionsMixin
# Sending Email
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .managers import PasswordResetCodeManager, UserManager
from ..base.api.constants import CUSTOMER_ROLE_SEED_DATA
from ..base.models import TimeStampedModel
from ..base.utils import short_data

logger = logging.getLogger(__name__)


class Roles(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    code_name = models.CharField(max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=1024, blank=True, null=True)
    is_active = models.BooleanField(default=True)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    first_name = models.CharField(max_length=128, blank=True, null=True, default='')
    middle_name = models.CharField(max_length=128, blank=True, null=True, default='')
    last_name = models.CharField(max_length=128, blank=True, null=True, default='')
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    mobile = models.CharField(max_length=128, blank=True, null=True)
    username = models.CharField(max_length=255, null=True, blank=True, unique=True)
    date_joined = models.DateField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_separated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    # Email address to be used as the username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', 'first_name']

    class Meta:
        verbose_name_plural = 'Users'

    def __str__(self):
        """Returns the email of the User when it is printed in the console"""
        return self.email if self.email else self.username

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name or short_data.get_first_name(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = self.first_name
        if self.middle_name:
            full_name += " " + self.middle_name
        if self.last_name:
            full_name += " " + self.last_name
        return full_name or ''


class AbstractBaseCode(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="User_Abstract", on_delete=models.PROTECT)
    code = models.CharField(_('code'), max_length=524)
    uid = models.CharField(max_length=40, default='uidrequired')
    timestamp = models.CharField(max_length=1024, default='timestamprequired')
    signature = models.CharField(max_length=1024, default='signaturerequired')

    class Meta:
        abstract = True

    def send_email(self, domain):
        PASSWORD_RESET_URL = domain + "/password-reset/"
        subject = "Reset Your Password"
        text_content = """Reset your password by clicking on this link:
                      %s{{ uid }}/{{ timestamp }}/{{ signature }}/{{  code }}
        """ % PASSWORD_RESET_URL

        # subject = render_to_string(subject_file).strip()
        from_email = settings.DEFAULT_EMAIL_FROM
        to = self.user.email
        # bcc_email = settings.DEFAULT_EMAIL_BCC

        # Make some context available
        ctxt = {
            'url': PASSWORD_RESET_URL,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'code': (self.code).decode(),
            'uid': self.uid,
            'timestamp': self.timestamp,
            'signature': self.signature

        }
        # text_content = render_to_string(txt_file, ctxt)
        html_content = render_to_string('email/password_reset.html', ctxt)
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            print("Email Sent succesfully")
        except Exception:
            logger.exception("Unable to send the mail.")

    def __unicode__(self):
        return "{0}, {1}, {2}, {3}".format(self.code, self.uid, self.timestamp, self.signature)


class PasswordResetCode(AbstractBaseCode):
    code = models.CharField(max_length=255)
    objects = PasswordResetCodeManager()

    def send_password_reset_email(self, domain):
        self.send_email(domain=domain)


class OTPLogin(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    mobile = models.CharField(max_length=15, null=True)
    otp = models.CharField(max_length=15, blank=True, null=True)
    counter = models.IntegerField(blank=True, default=25)
    is_active = models.BooleanField(default=True)
    resend_counter = models.IntegerField(blank=True, default=25)
