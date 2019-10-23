from django.conf import settings
from pyfcm import FCMNotification


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
        # print(data_message)
        registration_ids = list(users.exclude(device=None).values_list('device__token', flat=True))
        result = self.fcm.multiple_devices_data_message(registration_ids=registration_ids, data_message=data_message)
        # print(result)
        return result
