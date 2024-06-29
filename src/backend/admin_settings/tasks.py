import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from .models import ActivityLog

logger = get_task_logger(__name__)


@shared_task(bind=True)
def create_log(extra_key=None, record_by=None, user=[], new_data=None, previous_data=None, action_on=None,
               db_table=None, action_type=None):
    record_by = get_user_model().objects.filter(id=record_by, is_active=True).first() if record_by else None
    data = {
        "record_by": record_by if record_by else None,
        "created_by": record_by if record_by else None,
        "new_data": json.dumps(new_data) if new_data else None,
        "previous_data": json.dumps(previous_data) if previous_data else None,
        "is_active": True,
        "action_on": action_on,
        "db_table": db_table,
        "action_type": action_type
    }
    if len(user) > 0:
        for one_user in user:
            user = get_user_model().objects.filter(id=one_user, is_active=True).first() if user else None
            data["user"] = user if user else None
            ActivityLog.objects.create(**data)
    else:
        print(data)
        ActivityLog.objects.create(**data)
    return None
