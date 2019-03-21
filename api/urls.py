"""Urls"""

from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('messages/', views.ListCreateMessages.as_view(), name='messages'),
    path('messages/batch/', views.MessageBatchOperations.as_view(), name='messages_batch'),
    path('messages/<int:id>/', views.MessageDetail.as_view(), name='messages_id'),
    path('messages/<str:username>/', views.ListUserMessages.as_view(), name='messages_user'),
    path('users/', views.ListCreateApiUsers.as_view(), name='users'),
]
