from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from common.decorators import required_params
from ..models import Subscription, Class, ClassTime
from ..v1.views import UniversityAPIView as BaseUniversityAPIView


class UniversityAPIView(BaseUniversityAPIView):

    @required_params
    @action(methods=['post'], detail=False, url_path='diff')
    def diff_basename(self, request, timestamp, *args, **kwargs):
        result = super(UniversityAPIView, self).diff_basename(request, timestamp, *args, **kwargs)

        date_time = datetime.fromtimestamp(timestamp)
        prefix_user_path = request.user._meta.model_name
        related_user_path = f'{ClassTime.related_subscription_path}{prefix_user_path}'
        class_times_changes = ClassTime.objects. \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                  output_field=BooleanField()), u_id=F(related_user_path)). \
            filter(u_id=self.request.user.id). \
            values_list('changed', flat=True)

        if True in class_times_changes:
            result.data['base_names'].append(ClassTime.basename)

        result.data.update({'timestamp': int(datetime.timestamp(datetime.now()))})
        return result

    # TODO remove check after all users will update to version of API - v2
    @required_params
    @action(methods=['post'], detail=False)
    def migrations(self, request, token, *args, **kwargs):
        version = self.kwargs['version']
        user_device = self.request.user.device_set.filter(token=token, version='v1')

        if user_device.exists() and version == 'v2':
            user_subscriptions = Subscription.objects.filter(user=self.request.user)

            class_time_ids = list(ClassTime.objects.values_list('id', flat=True))
            class_ids = list(Class.objects.
                             filter(timetable__subgroup__subscription__in=user_subscriptions).
                             values_list('id', flat=True))

            result = [
                {
                    'basename': ClassTime.basename,
                    'ids': class_time_ids
                },
                {
                    'basename': Class.basename,
                    'ids': class_ids
                }
            ]

            user_device.update(version='v2', last_update=timezone.now())
            return Response(result)
        else:
            return Response(list())
