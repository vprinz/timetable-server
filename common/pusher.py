from django.conf import settings
from pyfcm import FCMNotification


class Pusher:

    @property
    def fcm(self):
        push_service = FCMNotification(api_key=settings.FIREBASE_API_KEY)
        return push_service

    def send_notification(self, users, updated_ids):
        message_title = 'Updating'
        data_message = {'ids': updated_ids}
        registration_id = 'eCTAgTQMrO0:APA91bFziRu1rUUAj0iiUuP-MhNT948vaEu9YRh5pacDUHzx_oJRuamGNdP1FGpSs3Kn9_UGsDsw1IbTLE62v5jn2fUILPsHBh84eHeOZkNA3OPFJd5uDK7vEmQ8pdxF0KK-rgUG4Kt-'
        result = self.fcm.single_device_data_message(registration_id=registration_id, data_message=data_message)
        print(result)
        return result
