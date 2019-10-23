from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from common.pusher import Pusher

post_bulk_update = Signal(providing_args=['updated_ids'])


def get_users_for_notification(model, ids):
    User = get_user_model()
    users_ids = model.objects.filter(id__in=ids).values_list(model.related_user_path, flat=True)
    users = User.objects.filter(id__in=users_ids)
    return users


@receiver(post_save)
def on_single_changes(sender, instance, **kwargs):
    from university.models import Subscription, Timetbale, Class, Lecturer

    models = [Subscription, Timetbale, Class, Lecturer]
    if sender in models:
        updated_ids = [instance.id]
        users = get_users_for_notification(sender, updated_ids)
        Pusher().send_notification(users, updated_ids, sender.basename)


@receiver(post_bulk_update)
def on_bulk_changes(sender, updated_ids, **kwargs):
    users = get_users_for_notification(sender, updated_ids)
    Pusher().send_notification(users, updated_ids, sender.basename)
