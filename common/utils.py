from enum import IntEnum

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


class TypeWeek(IntEnum):
    numerator = 0
    denominator = 1

    @classmethod
    def all(cls):
        return tuple((i.value, i.name.capitalize()) for i in cls)

    @classmethod
    def get_by_value(cls, value):
        if value > 1:
            return
        return cls.numerator.name.capitalize() if value == cls.numerator.value else cls.denominator.name.capitalize()
