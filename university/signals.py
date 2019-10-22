from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.dispatch import receiver

from common.pusher import Pusher

post_bulk_update = Signal(providing_args=['updated_ids'])


@receiver(post_bulk_update)
def on_changes(sender, updated_ids, **kwargs):
    User = get_user_model()
    users_ids = sender.objects.filter(id__in=updated_ids).values_list(sender.related_user_path, flat=True)
    users = User.objects.filter(id__in=users_ids).exclude(device=None)
    Pusher().send_notification(users, updated_ids)
