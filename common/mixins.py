from datetime import datetime

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .decorators import login_not_required, required_params


class LoginNotRequiredMixin:

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return login_not_required(view_func=view)


class SyncMixin:
    """Mixin for synchronization server's data with client."""

    @required_params
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def sync(self, request, already_handled, timestamp, *args, **kwargs):
        """
        Function for syncing content.

        :param already_handled: ids which have already been updated on client side.
        :param timestamp: the time at which the result is returned.
        :return: list of ids which were updated or deleted.
        """
        try:
            time = datetime.fromtimestamp(timestamp)
            result = self.queryset.model.get_ids_for_sync(self.get_queryset().exclude(id__in=already_handled), time)
            return Response(data=result)
        except Exception as e:
            return Response(data={'error': str(e)}, status=HTTP_400_BAD_REQUEST)

    def _get_meta_result(self, ids):
        queryset = self.get_queryset().filter(pk__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        return result

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def meta(self, request, *args, **kwargs):
        ids = set(request.data.get('ids', []))
        result = self._get_meta_result(ids)
        return Response(result, status=HTTP_200_OK)
