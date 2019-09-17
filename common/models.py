from django.db.models import Case, When, Value, BooleanField
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel


class CommonModel(TimeStampedModel):
    class Meta:
        abstract = True

    @classmethod
    def get_ids_for_sync(cls, queryset, date_time):
        query = queryset. \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)),
                                  default=Value(False), output_field=BooleanField())). \
            only('id', 'changed'). \
            values_list('id', 'changed')

        updated = set(row[0] for row in query if row[1])
        return {
            'updated': updated,
            'date_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
