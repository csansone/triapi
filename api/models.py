from django.db import models


class ApiUser(models.Model):
    """Simple user model to identify intended recipient of messages.
    Could be extended or replaced with a subclassed AbstractUser
    for additional functionality or authentication if needed."""

    username = models.CharField(max_length=32, null=False)
    username_lower = models.CharField(max_length=32, unique=True)

    def save(self, *args, **kwargs):
        self.username_lower = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


def get_default_user_id():
    user, created = ApiUser.objects.get_or_create(username='default')
    return user.id


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    fetched = models.BooleanField(default=False)
    content = models.CharField(max_length=1024, null=False)
    to_user = models.ForeignKey(ApiUser,
                                related_name='messages',
                                on_delete=models.CASCADE,
                                null=False,
                                default=get_default_user_id)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.content
