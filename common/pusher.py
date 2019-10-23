import logging

from django.conf import settings
from pyfcm import FCMNotification

log = logging.getLogger('informator')


class Pusher:

    @property
    def fcm(self):
        push_service = FCMNotification(api_key=settings.FIREBASE_API_KEY)
        return push_service

    def send_notification(self, users, updated_ids, basename):
        data_message = {
            'message_title': 'updating',
            'basename': basename,
            'ids': updated_ids
        }
        users_data = list(users.exclude(device=None).values('id', 'device__token'))
        for item in users_data:
            user_id = item['id']
            registration_id = item['device__token']
            data_message.update({'user_id': user_id})

            result = self.fcm.single_device_data_message(registration_id=registration_id, data_message=data_message)

            if result['failure'] > 0:
                push_error = dict()
                push_error.update({'token': registration_id, 'errors': result['results'], 'data_message': data_message})
                log.debug(f'Push error: {push_error}')
