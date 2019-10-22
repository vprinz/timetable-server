from django.conf import settings
from pyfcm import FCMNotification


class Pusher:

    @property
    def fcm(self):
        push_service = FCMNotification(api_key=settings.FIREBASE_API_KEY)
        return push_service

    def send_notification(self, users, updated_ids):
        message_title = 'updating'
        data_message = {'ids': updated_ids}
        registration_ids = list()
        for user in users:
            user_tokens = user.device_set.all().values_list('token', flat=True)
            for token in user_tokens:
                registration_ids.append(token)

        result = self.fcm.multiple_devices_data_message(registration_ids=registration_ids, data_message=data_message)
        print(result)
        return result
