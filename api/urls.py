"""Urls"""

from django.urls import path

from . import views

urlpatterns = [
    path('messages/', views.ListCreateMessages.as_view()),
    path('messages/batch/', views.MessageBatchOperations.as_view()),
    path('messages/<int:id>/', views.MessageDetail.as_view()),
    path('messages/<str:username>/', views.ListUserMessages.as_view()),
    path('users/', views.ListCreateApiUsers.as_view()),
]
