import secrets

from django.db import models
from django.utils import timezone
from datetime import timedelta


class Session(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    session_data = models.TextField(default="{}")
    expire_date = models.DateTimeField()

    @classmethod
    def create(cls):
        session_key = secrets.token_hex(20)
        expire_date = timezone.now() + timedelta(days=14)
        return cls.objects.create(
            session_key=session_key,
            expire_date=expire_date,
        )

    def is_expired(self):
        return timezone.now() >= self.expire_date
