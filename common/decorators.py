from functools import wraps

from django.utils.decorators import available_attrs
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST


def required_params(func):
    from inspect import signature, Parameter

    @wraps(func)
    def wrapper(*args, **kwargs):
        params = signature(func)
        names = [i.name for i in params.parameters.values() if i.kind == Parameter.POSITIONAL_OR_KEYWORD][2:]
        request = args[1]
        args = list(args[:2])
        for name in names:
            value = request.data.get(name, None)
            if value is None:
                return Response({name: ['required']}, status=HTTP_400_BAD_REQUEST)
            else:
                args.append(value)
        return func(*args, **kwargs)

    return wrapper


def login_not_required(view_func):
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.login_not_required = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
