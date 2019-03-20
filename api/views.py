"""Views"""

from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.response import Response

from api.models import ApiUser, Message
from .serializers import ApiUserSerializer, MessageSerializer


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint messages/<id>/
    GET single message detail
    DELETE single message
    """
    serializer_class = MessageSerializer

    # DRF forces URLs to use 'pk' if this is not set.
    lookup_field = 'id'

    def get_queryset(self):
        message_id = self.kwargs['id']
        queryset = Message.objects.filter(id=message_id)
        return queryset


class MessageBatchOperations(generics.UpdateAPIView):
    """Endpoint messages/batch/

    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        message_id_string = self.request.data['message_ids']
        message_ids = [int(i.strip()) for i in message_id_string.split(',')
                       if i.strip().isnumeric()]
        queryset = Message.objects.filter(id__in=message_ids)
        return queryset

    def patch(self, request, *args, **kwargs):
        action = request.data['action']
        queryset = self.get_queryset()

        if action == 'delete':
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif action == 'mark_as_read':
            qty = queryset.update(fetched=True)
            noun = 'message' if qty == 1 else 'messages'
            data = {'detail': '{} {} marked as read.'.format(qty, noun)}
            return Response(data, status=status.HTTP_200_OK)

        else:
            detail = 'Error message'
            raise ParseError(detail)


class ListCreateMessages(generics.ListCreateAPIView):
    """Endpoint messages/
    GET all messages
    POST new message
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.all()
        from_index = self.request.query_params.get('from_index', None)
        to_index = self.request.query_params.get('to_index', None)
        if from_index:
            queryset = queryset.filter(id__gte=from_index)
        if to_index:
            queryset = queryset.filter(id__lte=to_index)
        return queryset


class ListUserMessages(generics.ListCreateAPIView):
    """Endpoint messages/<username>/
    GET messages marked to username
    POST new message to username
    PATCH
    """
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        username = self.kwargs['username']
        try:
            _ = ApiUser.objects.get(username_lower=username.lower())
            return self.list(request, *args, **kwargs)
        except ApiUser.DoesNotExist:
            detail = 'Username {} does not exist.'.format(username)
            raise ParseError(detail=detail)

    def get_queryset(self):
        username = self.kwargs['username']
        from_index = self.request.query_params.get('from_index', None)
        to_index = self.request.query_params.get('to_index', None)
        unread = self.request.query_params.get('unread', None)

        queryset = Message.objects.filter(to_user__username_lower=username.lower())

        if from_index:
            queryset = queryset.filter(id__gte=from_index)
        if to_index:
            queryset = queryset.filter(id__lte=to_index)

        if unread == 'true':
            queryset = queryset.filter(fetched=False)

        return queryset

    def post(self, request, *args, **kwargs):
        username = self.kwargs['username']
        try:
            to_user = ApiUser.objects.get(username_lower=username.lower())

            # This line solves an issue where sometimes the data is a python dict
            # and sometimes it is an immutable queryset. -cas
            request.data._mutable = True

            request.data['to_user'] = to_user.id
            return self.create(request, *args, **kwargs)
        except ApiUser.DoesNotExist:
            raise ParseError('Username {} does not exist.'.format(username))


class ListCreateApiUsers(generics.ListCreateAPIView):
    serializer_class = ApiUserSerializer
    queryset = ApiUser.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        if len(username) < 1:
            detail = 'Value for "username" must be sent in POST body.'
            raise ParseError(detail)
        if ApiUser.objects.filter(username_lower=username.lower()).exists():
            detail = 'Username {} not available.'.format(username)
            raise ParseError(detail=detail)
        if username.isnumeric():
            detail = 'Username must not be entirely numeric. Use alphanumeric or all alpha.'
            raise ParseError(detail=detail)
        if not username.isalnum():
            detail = 'Username must be alphanumeric.'
            raise ParseError(detail=detail)
        return self.create(request, *args, **kwargs)
