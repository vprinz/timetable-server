from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
from rest_framework.decorators import action

from common.decorators import required_params
from university.models import ClassTime
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

    @action(methods=['post'], detail=False, url_path='diff')
    def migrations(self, request, *args, **kwargs):
        pass
