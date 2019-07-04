from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save
from django.dispatch import receiver

from common.utils import get_model_field_names
from university.models import Class


def get_changed_fields(instance):
    if instance.id is None:
        return
    else:
        changed_fields = []
        previous = Class.objects.get(id=instance.id)
        fields = get_model_field_names(Class)
        for field in fields:
            if getattr(previous, field, None) != getattr(instance, field, None):
                changed_fields.append(field)
        return changed_fields


@receiver(pre_save)
def on_change_timetable(sender, instance, **kwargs):
    print(sender)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'ntf', {
            'event': 'Changes of Timetable',
            'fields': get_changed_fields(instance)
        }
    )
