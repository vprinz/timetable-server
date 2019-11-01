from datetime import datetime

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from common.decorators import login_not_required
from common.decorators import required_params

import logging

log = logging.getLogger('informator')


class LoginNotRequiredMixin:

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return login_not_required(view_func=view)


class SyncMixin:
    """
        Mixin for synchronization server's data with client.
        Fields:
            - sync_queryset: queryset without filter() or exclude(). Just virgin queryset for working with all data.
    """
    sync_queryset = None

    @required_params
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def sync(self, request, already_handled, timestamp, *args, **kwargs):
        """
        :param already_handled: ids which have already been updated on client side.
        :param timestamp: the time at which the result is returned.
        :return: list of ids which were updated or deleted.
        """
        try:
            date_time = datetime.fromtimestamp(timestamp)
            result = self.queryset.model.get_ids_for_sync(self.sync_queryset.exclude(id__in=already_handled), date_time)
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
        """
        :return: a list with an information of all instances that belongs to certain model.
        """
        ids = set(request.data.get('ids', []))
        log.debug(f'IDS: {ids} ||| SESSION: {request.session.session_key} ||| {request.user}')
        result = self._get_meta_result(ids)
        log.debug((f'RESULT: {result}'))
        log.debug('=======================================')
        return Response(result, status=HTTP_200_OK)
