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
    basename = None
    related_user_path = None

    class Meta:
        abstract = True

    @classmethod
    def get_ids_for_sync(cls, queryset, existing_ids, date_time):
        query = queryset. \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)),
                                  default=Value(False), output_field=BooleanField())). \
            values_list('id', 'changed')

        all_ids = set(row[0] for row in query)
        updated = set(row[0] for row in query if row[1])
        return {
            'updated_ids': updated,
            'deleted_ids': set(existing_ids) - all_ids
        }
