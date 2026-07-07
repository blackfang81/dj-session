from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Session(models.Model):
    session_key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"