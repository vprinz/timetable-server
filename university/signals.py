from django.dispatch import Signal
from django.dispatch import receiver

from common.pusher import Pusher

post_bulk_update = Signal(providing_args=['updated_ids'])


@receiver(post_bulk_update)
def on_changes(sender, updated_ids, **kwargs):
    Pusher().send_notification([], updated_ids)
