"""Serializers"""

from rest_framework import serializers
from api.models import ApiUser, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'created_at',
            'content',
            'fetched',
            'to_user',
        )
        model = Message


class ApiUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
        )
        model = ApiUser
