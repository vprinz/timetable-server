from datetime import datetime

from django.db.models import Case, When, Value, BooleanField
from django.db.models.query import QuerySet as BaseQuerySet
from django_extensions.db.models import TimeStampedModel

from university.signals import post_bulk_update


class QuerySet(BaseQuerySet):

    def bulk_update(self, objs, fields, batch_size=None):
        super(QuerySet, self).bulk_update(objs, fields, batch_size)
        post_bulk_update.send(sender=objs[0].__class__, updated_ids=[obj.id for obj in objs])


class CommonModel(TimeStampedModel):
    objects = QuerySet.as_manager()

    class Meta:
        abstract = True

    @classmethod
    def get_ids_for_sync(cls, queryset, date_time):
        query = queryset. \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)),
                                  default=Value(False), output_field=BooleanField())). \
            values('id', 'changed', 'created', 'modified')

        added = set(row['id'] for row in query if
                    row['created'].replace(microsecond=0) == row['modified'].replace(microsecond=0))
        updated = set(row['id'] for row in query if row['changed'])
        return {
            'added_ids': added,
            'updated_ids': updated - added,
            'timestamp': datetime.timestamp(datetime.now())
        }
