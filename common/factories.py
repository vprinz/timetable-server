from datetime import datetime

import factory.fuzzy
import pytz


class CommonFactory(factory.DjangoModelFactory):
    created = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))
    modified = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))

    class Meta:
        abstract = True
