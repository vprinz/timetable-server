from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.db.models import F

from common.pusher import Pusher

post_bulk_update = Signal(providing_args=['updated_ids'])


def _prepare_data_for_sending(model, ids):
    # data = {'user_id': None, 'device_token': None, 'noisy_ids': list(), 'silent_ids': list()}

    # User = get_user_model()
    # users_ids = model.objects.filter(id__in=ids).values_list(model.related_user_path, flat=True)
    # users = User.objects.filter(id__in=users_ids)

    subscription_is_main_path = f'{model.related_subscription_path}__is_main'
    user_device_path = f'{model.related_user_path}__device'
    user_device_token_path = f'{user_device_path}__token'
    query = model.objects. \
        annotate(user_id=F(model.related_user_path), subscription_is_main=F(subscription_is_main_path),
                 user_device=F(user_device_path), device_token=F(user_device_token_path)). \
        filter(id__in=ids).exclude(user_device=None). \
        values('id', 'user_id', 'subscription_is_main', 'device_token')
    print(query)
    result = list()
    for item in query:
        data = dict()
        data['user_id'] = item['user_id']
        data['device_token'] = item['device_token']
        data['noisy_ids'] = item['id'] if item['subscription_is_main'] else list()
        data['silent_ids'] = item['id'] if not item['subscription_is_main'] else list()
        result.append(data)

    for i in result:
        print(i)

    return result


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
    _prepare_data_for_sending(sender, updated_ids)
    users = get_users_for_notification(sender, updated_ids)
    Pusher().send_notification(users, updated_ids, sender.basename)
