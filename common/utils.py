from enum import IntEnum
from itertools import chain

from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, APIException):
        if isinstance(exc.detail, (list, dict)):
            response.data = exc.get_codes()
        else:
            response.data['detail'] = exc.get_codes()

    return response


def get_model_field_names(model):
    """
    Replaces outdated method MyModel._meta.get_all_field_names() (removed in Django 1.10).

    For details see Django 1.10 version of this file:
        https://github.com/django/django/blob/master/docs/ref/models/meta.txt
    """
    return list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in model._meta.get_fields()
        if not (field.many_to_one and field.related_model is None)
    )))


class TypeWeek(IntEnum):
    numerator = 0
    denominator = 1

    @classmethod
    def all(cls):
        return tuple((i.value, i.name.capitalize()) for i in cls)

    @classmethod
    def data(cls):
        return {i.value for i in cls}

    @classmethod
    def get_by_value(cls, value):
        if value > 1:
            return
        return cls.numerator.name.capitalize() if value == cls.numerator.value else cls.denominator.name.capitalize()

    @classmethod
    def get_reversed(cls, value):
        """
        Changing current_type_of_week for faculty to opposite.
        :param value: current type of week value.
        :return: reversed type of week.
        """
        all = cls.data()
        value = {value}
        return all.difference(value).pop()
