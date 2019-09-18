from django.dispatch import Signal
from django.dispatch import receiver
from pyfcm import FCMNotification

post_bulk_update = Signal(providing_args=['updated_ids'])


@receiver(post_bulk_update)
def on_change_timetable(sender, updated_ids, **kwargs):
    push_service = FCMNotification(
        api_key="AAAAwM-KH_A:APA91bFx9ME75i39O6Dv7pUxXNm4dx86PLgt7aZk3a_vcnoQ3YJTYATes9xF4JAs4XhILvc1pnarFis2vVPa9J7Q9WaPWFJZGpj9hInlzwMlU9Z9w30nPElq-ljRXrI-_lbEBHL_R0Gx")

    registration_id = 'eCTAgTQMrO0:APA91bFziRu1rUUAj0iiUuP-MhNT948vaEu9YRh5pacDUHzx_oJRuamGNdP1FGpSs3Kn9_UGsDsw1IbTLE62v5jn2fUILPsHBh84eHeOZkNA3OPFJd5uDK7vEmQ8pdxF0KK-rgUG4Kt-'

    message_title = "РАБОТАЕТ"

    data_message = {'updated_ids': updated_ids}

    result = push_service.single_device_data_message(registration_id=registration_id, data_message=data_message)

    print(result)
