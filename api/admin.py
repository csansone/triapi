from django.contrib import admin
from .models import ApiUser, Message

# Register your models here.

admin.site.register(ApiUser)
admin.site.register(Message)
