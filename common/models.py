from django.db.models import Case, When, Value, BooleanField, SmallIntegerField
from django.db.models.query import QuerySet as BaseQuerySet
from django_extensions.db.models import TimeStampedModel

from university.signals import post_bulk_update


class QuerySet(BaseQuerySet):

    def bulk_update(self, objs, fields, batch_size=None):
        super(QuerySet, self).bulk_update(objs, fields, batch_size)
        post_bulk_update.send(sender=objs[0].__class__, updated_ids=[obj.id for obj in objs])


class CommonModel(TimeStampedModel):
    ACTIVE = 0
    DELETED = 1
    STATES = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
    )

    state = SmallIntegerField(default=ACTIVE, choices=STATES)

    objects = QuerySet.as_manager()
    basename = None

    # TODO: refactor
    related_subscription_path = str()

    class Meta:
        abstract = True

    @classmethod
    def get_ids_for_sync(cls, queryset, date_time):
        query = queryset. \
            filter(state=cls.ACTIVE). \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)),
                                  default=Value(False), output_field=BooleanField())). \
            values('id', 'changed')

        updated_ids = set(row['id'] for row in query if row['changed'])
        deleted_ids = list(queryset.filter(state=cls.DELETED, modified__gt=date_time).values_list('id', flat=True))
        return {
            'updated_ids': updated_ids,
            'deleted_ids': deleted_ids
        }

    def safe_delete(self):
        self.state = self.DELETED
        self.save()

    def silent_save(self, data):
        """
        Method for saving instance without sending pushes.
        :param data: dictionary of changed parameters.
        """
        self.__class__.objects.filter(id=self.id).update(**data)
