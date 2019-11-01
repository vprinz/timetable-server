import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from common.pusher import Pusher

log = logging.getLogger('informator')

post_bulk_update = Signal(providing_args=['updated_ids'])


def get_users_for_notification(model, ids):
    User = get_user_model()
    users_ids = model.objects.filter(id__in=ids). \
        values_list(f'{model.related_subscription_path}{User._meta.model_name}', flat=True)
    users = User.objects.filter(id__in=users_ids)
    return users


@receiver(post_save)
def on_single_changes(sender, instance, **kwargs):
    from university.models import Subscription, Timetable, Class, Lecturer
    models = [Subscription, Timetable, Class, Lecturer]
    if sender in models:
        log.debug(f'INSTANCE WEEKDAY {instance.weekday}')
        updated_ids = [instance.id]
        users = get_users_for_notification(sender, updated_ids)
        transaction.on_commit(Pusher().send_notification(sender, users, updated_ids))


@receiver(post_bulk_update)
def on_bulk_changes(sender, updated_ids, **kwargs):
    users = get_users_for_notification(sender, updated_ids)
    Pusher().send_notification(sender, users, updated_ids)
