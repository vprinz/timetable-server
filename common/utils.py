from itertools import chain

from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, APIException):
        response.data = exc.get_full_details()

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
