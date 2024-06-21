import logging
import os
import os.path

# Sending Email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send(to, subject, html_body, text_body=None, attachments=[], from_email=None, cc=None, bcc=None):
    if not (isinstance(to, list) or isinstance(to, tuple)):
        to = [to]

    # Remove empty items
    to = [x for x in to if x not in (None, "")]

    if text_body is None:
        text_body = strip_tags(html_body)

    # Convert CC into a list
    if cc and not (isinstance(cc, list) or isinstance(cc, tuple)):
        cc = [cc]

    # Convert BCC into a list
    if bcc and not (isinstance(bcc, list) or isinstance(bcc, tuple)):
        bcc = [bcc]

    # if bcc is None, set a default email as bcc
    if not bcc:
        bcc = []

    try:
        msg = EmailMultiAlternatives(subject, text_body, to=to)
        if cc:
            msg.cc = cc

        if bcc:
            msg.bcc = bcc

        if from_email:
            msg.from_email = from_email

        msg.attach_alternative(html_body, "text/html")
        for attachment in attachments:
            if attachment:
                # Try to get only filename from full-path
                try:
                    attachment.open()
                except Exception as e:
                    print(str(e))
                attachment_name = os.path.split(attachment.name)[-1]
                msg.attach(attachment_name or attachment.name, attachment.read())
        msg.send()
        return True
    except Exception:
        logger.exception("Unable to send the mail.")
        return False


def send_from_template(to, subject, template, context, **kwargs):
    # print template
    html_body = render_to_string(template, context)
    return send(to, subject, html_body, **kwargs)
