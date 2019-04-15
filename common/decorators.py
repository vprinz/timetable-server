from functools import wraps

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
                return Response({name: "Это поле обязательно."}, status=HTTP_400_BAD_REQUEST)
            else:
                args.append(value)
        return func(*args, **kwargs)
    return wrapper